#include <string>

// Definition for singly-linked list.
struct ListNode
{
	int val;
	ListNode *next;
	ListNode() : val(0), next(nullptr) {}
	ListNode(int x) : val(x), next(nullptr) {}
	ListNode(int x, ListNode *next) : val(x), next(next) {}
};

class Solution
{
public:
	ListNode *addTwoNumbers(ListNode *l1, ListNode *l2)
	{
		return addTwoNumbers_v1(l1, l2);
		return addTwoNumbers_v0(l1, l2);
	}

	ListNode *addTwoNumbers_v1(ListNode *l1, ListNode *l2)
	{
		ListNode *head = l1;

		int carry = 0;

		while (true)
		{
			int sum = (l1 ? l1->val : 0) + (l2 ? l2->val : 0) + carry;
			carry = (sum >= 10);
			// printf("sum = %d, carry = %d\n", sum, carry);

			l1->val = sum % 10;
			if (!l1->next) // l2 is maybe longer than l1
			{
				l1->next = l2->next;
				break;
			}
			if (!l2->next) // l2 is maybe shorter than l1
			{
				break;
			}

			l1 = l1->next;
			l2 = l2->next;
		}

		// l2 here is not relevant and we only need to finish processing l1 with respect to carry
		while (l1->next)
		{
			int sum = l1->next->val + carry;
			carry = (sum >= 10);

			l1->next->val = sum % 10;

			l1 = l1->next;
		}

		if (carry)
		{
			l1->next = new ListNode(carry);
		}

		return head;
	}

	ListNode *addTwoNumbers_v0(ListNode *l1, ListNode *l2)
	{
		int carry = 0;

		ListNode *head = nullptr;
		ListNode *last = nullptr;

		while (l1 || l2)
		{
			int sum = (l1 ? l1->val : 0) + (l2 ? l2->val : 0) + carry;
			carry = (sum >= 10);
			// printf("sum = %d, carry = %d\n", sum, carry);

			ListNode *new_item = new ListNode(sum % 10);
			if (last)
			{
				last->next = new_item;
				last = new_item;
			}
			else
			{
				last = new_item;
				head = last;
			}

			if (l1)
				l1 = l1->next;

			if (l2)
				l2 = l2->next;
		}

		if (carry)
		{
			last->next = new ListNode(carry);
			last = last->next;
		}

		return head;
	}
};

ListNode *number_to_list(std::string const &s)
{
	ListNode *head = nullptr;
	for (auto ch : s)
	{
		ListNode *new_head = new ListNode(ch - '0');
		new_head->next = head;
		head = new_head;
	}
	return head;
}

std::string list_to_number(ListNode *head)
{
	std::string result;
	while (head)
	{
		result.insert(result.end(), (char)head->val + '0');
		head = head->next;
	}
	return {result.rbegin(), result.rend()};
}

std::string list_to_string(ListNode *head)
{
	std::string result;
	result += "[";
	while (head)
	{
		result.insert(result.end(), (char)head->val + '0');
		if (head->next)
			result += ", ";
		head = head->next;
	}
	result += ']';
	return std::move(result);
}

void run_test(std::string n1, std::string n2, std::string expected)
{
	ListNode *l1 = number_to_list(n1);
	ListNode *l2 = number_to_list(n2);

	printf("input_1: %s -> %s\n", n1.c_str(), list_to_string(l1).c_str());
	printf("input_2: %s -> %s\n", n2.c_str(), list_to_string(l2).c_str());

	Solution s;
	ListNode *result = s.addTwoNumbers(l1, l2);

	std::string const result_str = list_to_number(result);
	printf("result: %s = %s\n", result_str.c_str(), list_to_string(result).c_str());
	printf("expected: %s\n", expected.c_str());
	printf("%s\n", (expected == result_str) ? "OK" : "ERROR");
	printf("\n");
}

int main()
{
	run_test("0", "0", "0");
	run_test("123", "0", "123");
	run_test("123", "78", "201");
	run_test("342", "465", "807");
	run_test("9999999", "9999", "10009998");
}