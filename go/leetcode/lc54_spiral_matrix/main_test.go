package main

import (
	tu "antoxa/leetcode/testutil"
	"testing"
)

func spiralOrder_ugly(matrix [][]int) (result []int) {
	if len(matrix) == 0 || len(matrix[0]) == 0 {
		return []int{}
	}

	ROWS := len(matrix)
	COLS := len(matrix[0])

	row_min, row_max := 0, ROWS
	col_min, col_max := 0, COLS

	res_append := func(i *int, val int) {
		(*i)++
		result = append(result, val)
	}

	for i := 0; i < ROWS*COLS; /**/ {
		// go right
		for col := col_min; col < col_max && i < ROWS*COLS; col++ {
			res_append(&i, matrix[row_min][col])
		}

		// transition right -> down
		row_min++

		// go down
		for row := row_min; row < row_max && i < ROWS*COLS; row++ {
			res_append(&i, matrix[row][col_max-1])
		}

		// transition down -> left
		col_max--

		// go left
		for col := col_max - 1; col >= col_min && i < ROWS*COLS; col-- {
			res_append(&i, matrix[row_max-1][col])
		}

		// transition left -> up
		row_max--

		// go up
		for row := row_max - 1; row >= row_min && i < ROWS*COLS; row-- {
			res_append(&i, matrix[row][col_min])
		}

		// transition up -> right
		col_min++
	}
	return
}

func spiralOrder_with_direction(matrix [][]int) (result []int) {
	if len(matrix) == 0 || len(matrix[0]) == 0 {
		return []int{}
	}

	ROWS := len(matrix)
	COLS := len(matrix[0])

	row_min, row_max := 0, ROWS
	col_min, col_max := 0, COLS

	type directionT int
	const (
		direction_Right directionT = iota
		direction_Down
		direction_Left
		direction_Up
	)
	direction := direction_Right

	row, col := 0, 0

	for range ROWS * COLS {
		result = append(result, matrix[row][col])

		switch direction {
		case direction_Right:
			if col < col_max-1 {
				col++
			} else {
				row_min++
				row++
				direction = direction_Down
			}
		case direction_Down:
			if row < row_max-1 {
				row++
			} else {
				col_max--
				col--
				direction = direction_Left
			}
		case direction_Left:
			if col > col_min {
				col--
			} else {
				row_max--
				row--
				direction = direction_Up
			}
		case direction_Up:
			if row > row_min {
				row--
			} else {
				col_min++
				col++
				direction = direction_Right
			}
		}
	}

	return
}

// similar to _direction, but generalize bounds
// this becomes too cimplicated quickly tbh.
// the logic to change bounaries together with change of direction
// needs to ideally come from the movement vector itself and only it
// ended up with complex code for no gain
func spiralOrder_with_vector(matrix [][]int) (result []int) {
	if len(matrix) == 0 || len(matrix[0]) == 0 {
		return []int{}
	}

	ROWS := len(matrix)
	COLS := len(matrix[0])

	row_min, row_max := 0, ROWS
	col_min, col_max := 0, COLS

	type dir struct {
		dx int // cols
		dy int // rows
	}
	var (
		d_Right = dir{1, 0}
		d_Down  = dir{0, 1}
		d_Left  = dir{-1, 0}
		d_Up    = dir{0, -1}
		dirs    = []dir{d_Right, d_Down, d_Left, d_Up}
	)

	direction_idx := 0
	row, col := 0, 0

	move := func(r, c int, d dir) (nr, nc int) {
		return r + d.dy, c + d.dx
	}

	canMove := func(r, c int, d dir) bool {
		nr, nc := move(r, c, d)
		if !(row_min <= nr && nr < row_max) {
			return false
		}
		if !(col_min <= nc && nc < col_max) {
			return false
		}
		return true
	}

	for range ROWS * COLS {
		result = append(result, matrix[row][col])

		if !canMove(row, col, dirs[direction_idx]) {
			switch dirs[direction_idx] {
			case d_Right:
				row_min++
			case d_Down:
				col_max--
			case d_Left:
				row_max--
			case d_Up:
				col_min++
			}
			direction_idx = (direction_idx + 1) % len(dirs)
		}
		row, col = move(row, col, dirs[direction_idx])
	}

	return
}

var testData = []tu.TestData[[][]int, []int]{
	{
		Input:    [][]int{{1, 2, 3}, {4, 5, 6}, {7, 8, 9}},
		Expected: []int{1, 2, 3, 6, 9, 8, 7, 4, 5},
	},
	{
		Input:    [][]int{{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}},
		Expected: []int{1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7},
	},
	{
		Input: [][]int{
			{1, 2, 3, 4},
			{5, 6, 7, 8},
			{9, 10, 11, 12},
			{13, 14, 15, 16},
			{17, 18, 19, 20},
			{21, 22, 23, 24},
		},
		Expected: []int{1, 2, 3, 4, 8, 12, 16, 20, 24, 23, 22, 21, 17, 13, 9, 5, 6, 7, 11, 15, 19, 18, 14, 10},
	},
}

func TestSpiralMatrix(t *testing.T) {
	t.Run("ugly", func(t *testing.T) { tu.RunTest(t, spiralOrder_ugly, testData) })
	t.Run("with_direction", func(t *testing.T) { tu.RunTest(t, spiralOrder_with_direction, testData) })
	t.Run("with_vector", func(t *testing.T) { tu.RunTest(t, spiralOrder_with_vector, testData) })
}
