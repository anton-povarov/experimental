/*
 * extract_arm64_functions.c
 *
 * Usage:
 *   cc -std=c11 -O2 extract_arm64_functions.c -o extract_arm64_functions
 *   ./extract_arm64_functions <mach-o-binary>
 *
 * Produces files in ./funcs/ named like "<index>_<sanitized_symbol>.bin"
 *
 * Notes:
 *  - Assumes 64-bit Mach-O slice (ARM64). If the input is a FAT (universal)
 *    binary, it picks the first ARM64 slice it finds.
 *  - Assumes symbol table exists (binary not stripped).
 *  - Does not attempt to demangle Swift names; it will sanitize them for filenames.
 *  - Uses nlist_64 and section number matching: selects symbols where n_type is N_SECT
 *    and n_sect == the __text section's global section index.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <mach-o/loader.h>
#include <mach-o/fat.h>
#include <mach-o/nlist.h>
#include <arpa/inet.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>

#define ERR(msg)     \
	do               \
	{                \
		perror(msg); \
		exit(1);     \
	} while (0)

struct sym_entry
{
	char *name;
	uint64_t va;
	uint64_t fileoff;
	uint64_t size; // computed later
};

static char *sanitize_name(const char *s)
{
	size_t n = strlen(s);
	// strip leading underscore for nicer names (optional)
	const char *start = s;
	if (s[0] == '_')
		start = s + 1;
	// allocate sanitized result
	char *out = malloc(n + 1);
	if (!out)
		return NULL;
	size_t oi = 0;
	for (size_t i = 0; start[i] && oi < n; ++i)
	{
		char c = start[i];
		if (isalnum((unsigned char)c) || c == '_' || c == '-' || c == '.')
		{
			out[oi++] = c;
		}
		else
		{
			out[oi++] = '_';
		}
	}
	if (oi == 0)
	{
		strcpy(out, "unnamed");
	}
	else
	{
		out[oi] = '\0';
	}
	return out;
}

// sort symbols by VA ascending
int cmp_sym(const void *a, const void *b)
{
	const struct sym_entry *sa = a;
	const struct sym_entry *sb = b;
	if (sa->va < sb->va)
		return -1;
	if (sa->va > sb->va)
		return 1;
	return 0;
}

int main(int argc, char **argv)
{
	if (argc != 2)
	{
		fprintf(stderr, "Usage: %s <mach-o-binary>\n", argv[0]);
		return 1;
	}

	const char *filename = argv[1];
	int fd = open(filename, O_RDONLY);
	if (fd < 0)
		ERR("open");

	struct stat st;
	if (fstat(fd, &st) < 0)
		ERR("fstat");

	uint8_t *map = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
	if (map == MAP_FAILED)
		ERR("mmap");
	close(fd);

	const uint8_t *base = map;
	const uint8_t *macho = base;
	bool is_fat = false;

	uint32_t magic = *(uint32_t *)base;
	if (magic == FAT_MAGIC || magic == FAT_CIGAM)
	{
		is_fat = true;
		struct fat_header *fh = (struct fat_header *)base;
		uint32_t narch = ntohl(fh->nfat_arch);
		struct fat_arch *arch = (struct fat_arch *)(fh + 1);
		bool found = false;
		for (uint32_t i = 0; i < narch; i++)
		{
			uint32_t cputype = ntohl(arch[i].cputype);
			// CPU_TYPE_ARM64 is CPU_TYPE_ARM | CPU_ARCH_ABI64; value 0x0100000c? use constant:
			// We compare against CPU_TYPE_ARM64 numeric value if available.
			// For portability, check known values:
			// CPU_TYPE_ARM64 == 0x0100000c == 16777228
			if ((int32_t)cputype == CPU_TYPE_ARM64 || (int32_t)cputype == 16777228)
			{
				uint32_t off = ntohl(arch[i].offset);
				uint32_t size = ntohl(arch[i].size);
				if (off + (uint32_t)size <= (uint32_t)st.st_size)
				{
					macho = base + off;
					found = true;
					break;
				}
			}
		}
		if (!found)
		{
			fprintf(stderr, "No arm64 slice found in FAT binary\n");
			munmap(map, st.st_size);
			return 1;
		}
	}

	struct mach_header_64 *mh = (struct mach_header_64 *)macho;
	if (mh->magic != MH_MAGIC_64)
	{
		fprintf(stderr, "Not a 64-bit Mach-O slice (magic=0x%x)\n", mh->magic);
		munmap(map, st.st_size);
		return 1;
	}

	// Walk load commands; we need:
	// - the __TEXT,__text section and its file offset/addr/size
	// - the section's global section index (sections are numbered starting at 1 across LC_SEGMENT_64 in order)
	// - the LC_SYMTAB command
	struct load_command *lc = (struct load_command *)(macho + sizeof(struct mach_header_64));
	struct section_64 *text_sect = NULL;
	uint32_t text_sect_index = 0;
	struct symtab_command *symtab = NULL;

	uint32_t sect_counter = 0; // global section numbering starts at 1
	for (uint32_t i = 0; i < mh->ncmds; i++)
	{
		if ((uint8_t *)lc + sizeof(struct load_command) > (macho + st.st_size))
		{
			fprintf(stderr, "Load command pointer out of range\n");
			munmap(map, st.st_size);
			return 1;
		}
		if (lc->cmd == LC_SEGMENT_64)
		{
			struct segment_command_64 *seg = (struct segment_command_64 *)lc;
			struct section_64 *sect = (struct section_64 *)(seg + 1);
			for (uint32_t j = 0; j < seg->nsects; j++)
			{
				sect_counter++;
				if (strcmp(sect[j].segname, "__TEXT") == 0 &&
					strcmp(sect[j].sectname, "__text") == 0)
				{
					text_sect = &sect[j];
					text_sect_index = sect_counter; // n_sect values are 1-based index into all sections
				}
			}
		}
		else if (lc->cmd == LC_SYMTAB)
		{
			symtab = (struct symtab_command *)lc;
		}
		lc = (struct load_command *)((uint8_t *)lc + lc->cmdsize);
	}

	if (!text_sect)
	{
		fprintf(stderr, "Could not find __TEXT,__text section\n");
		munmap(map, st.st_size);
		return 1;
	}

	if (!symtab)
	{
		fprintf(stderr, "No symbol table (LC_SYMTAB) present — binary likely stripped\n");
		munmap(map, st.st_size);
		return 1;
	}

	// bounds check symtab offsets
	if (symtab->symoff == 0 || symtab->stroff == 0)
	{
		fprintf(stderr, "Empty symtab/strtab\n");
		munmap(map, st.st_size);
		return 1;
	}
	if (symtab->symoff + symtab->nsyms * sizeof(struct nlist_64) > (uint32_t)st.st_size)
	{
		fprintf(stderr, "Symbol table out of file bounds\n");
		munmap(map, st.st_size);
		return 1;
	}
	if (symtab->stroff >= (uint32_t)st.st_size)
	{
		fprintf(stderr, "String table out of file bounds\n");
		munmap(map, st.st_size);
		return 1;
	}

	struct nlist_64 *nlist = (struct nlist_64 *)(macho + symtab->symoff);
	const char *strtab = (const char *)(macho + symtab->stroff);

	// Collect symbols that are in the __text section
	struct sym_entry *syms = calloc(symtab->nsyms, sizeof(struct sym_entry));
	if (!syms)
		ERR("calloc");
	size_t sym_count = 0;

	for (uint32_t i = 0; i < symtab->nsyms; i++)
	{
		struct nlist_64 *n = &nlist[i];
		// skip STAB (debug) symbols
		if (n->n_type & N_STAB)
			continue;
		// must be in a section
		if ((n->n_type & N_TYPE) != N_SECT)
			continue;
		if (n->n_sect != text_sect_index)
			continue;

		// string index check
		if (n->n_un.n_strx == 0)
			continue;
		const char *name = strtab + n->n_un.n_strx;
		// simple bounds safe check
		if ((const uint8_t *)name >= map + st.st_size)
			continue;

		uint64_t va = n->n_value;
		// ensure the VA lies within the text section virtual address range
		if (va < text_sect->addr || va >= text_sect->addr + text_sect->size)
		{
			// skip symbols outside __text
			continue;
		}

		uint64_t fileoff = va - text_sect->addr + text_sect->offset;
		if (fileoff >= (uint64_t)st.st_size)
			continue;

		syms[sym_count].name = strdup(name);
		syms[sym_count].va = va;
		syms[sym_count].fileoff = fileoff;
		syms[sym_count].size = 0;
		sym_count++;
	}

	if (sym_count == 0)
	{
		fprintf(stderr, "No symbols located in __TEXT,__text (section index %u)\n", text_sect_index);
		free(syms);
		munmap(map, st.st_size);
		return 1;
	}

	qsort(syms, sym_count, sizeof(struct sym_entry), cmp_sym);

	// compute sizes: gap to next symbol, last one uses section end
	uint64_t sect_end_va = text_sect->addr + text_sect->size;
	for (size_t i = 0; i < sym_count; i++)
	{
		uint64_t this_va = syms[i].va;
		uint64_t next_va = (i + 1 < sym_count) ? syms[i + 1].va : sect_end_va;
		if (next_va <= this_va)
		{
			syms[i].size = 0;
		}
		else
		{
			syms[i].size = next_va - this_va;
		}
		// sanity cap by section boundary
		if (this_va + syms[i].size > sect_end_va)
		{
			syms[i].size = sect_end_va - this_va;
		}
	}

	// prepare output directory
	const char *outdir = "funcs";
	if (mkdir(outdir, 0755) != 0)
	{
		if (errno != EEXIST)
		{
			perror("mkdir");
			// continue even if mkdir fails (maybe exists)
		}
	}

	// write each function's bytes to a file
	for (size_t i = 0; i < sym_count; i++)
	{
		if (syms[i].size == 0)
			continue;
		// sanitize name
		char *sname = sanitize_name(syms[i].name);
		if (!sname)
			sname = strdup("sym");

		char outpath[4096];
		snprintf(outpath, sizeof(outpath), "%s/%04zu_%s.bin", outdir, i, sname);

		FILE *f = fopen(outpath, "wb");
		if (!f)
		{
			fprintf(stderr, "Failed to open %s for writing: %s\n", outpath, strerror(errno));
			free(sname);
			continue;
		}
		// check fileoff + size in bounds
		if (syms[i].fileoff + syms[i].size > (uint64_t)st.st_size)
		{
			fprintf(stderr, "Symbol %s out of bounds (fileoff+size > file)\n", syms[i].name);
			fclose(f);
			free(sname);
			continue;
		}

		size_t written = fwrite(map + syms[i].fileoff, 1, (size_t)syms[i].size, f);
		if (written != syms[i].size)
		{
			fprintf(stderr, "Short write for %s: wrote %zu of %llu\n", outpath, written, (unsigned long long)syms[i].size);
		}
		else
		{
			printf("Wrote %s  (VA=0x%llx size=%llu)\n", outpath, (unsigned long long)syms[i].va, (unsigned long long)syms[i].size);
		}
		fclose(f);
		free(sname);
	}

	// cleanup
	for (size_t i = 0; i < sym_count; i++)
		free(syms[i].name);
	free(syms);
	munmap(map, st.st_size);
	return 0;
}
