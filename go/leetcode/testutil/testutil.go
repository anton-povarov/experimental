package testutil

import (
	"fmt"
	"reflect"
	"testing"

	"github.com/fatih/color"
	"github.com/tiendc/go-deepcopy"
)

func isOK[T any](result, expected T) bool {
	return reflect.DeepEqual(result, expected)
}

func isOKStr[T any](result, expected T) string {
	if reflect.DeepEqual(result, expected) {
		return "OK"
	}
	return "ERROR"
}

type TestData[T any, E any] struct {
	Input    T
	Expected E
}

func do_deepcopy[T any](src T) (dst T) {
	err := deepcopy.Copy(&dst, &src)
	if err != nil {
		panic("deepcopy error: " + err.Error())
	}
	return
}

func RunTest[T any, E any](t *testing.T, testedFunc func(T) E, data []TestData[T, E]) {
	green := color.New(color.FgGreen)
	red := color.New(color.FgHiRed)

	for _, d := range data {
		result := testedFunc(do_deepcopy(d.Input))

		test_ok := reflect.DeepEqual(result, d.Expected)
		if !test_ok {
			t.Fail()
		}

		clr := func() *color.Color {
			if test_ok {
				return green
			}
			return red
		}()

		if !test_ok || testing.Verbose() {
			clr.EnableColor() // this is required as go test does shenanigans with colored output
			fmt.Fprintln(t.Output(),
				clr.Sprintf("[%s] %#v -> %#v, expected: %#v", isOKStr(result, d.Expected), d.Input, result, d.Expected))
			clr.DisableColor()
		}
	}
}

type TestData2[T1 any, T2 any, E any] struct {
	Input1   T1
	Input2   T2
	Expected E
}

func RunTest2[T1 any, T2 any, E any](t *testing.T, testedFunc func(T1, T2) E, data []TestData2[T1, T2, E]) {
	green := color.New(color.FgGreen)
	red := color.New(color.FgHiRed)

	for _, d := range data {
		result := testedFunc(do_deepcopy(d.Input1), do_deepcopy(d.Input2))

		test_ok := reflect.DeepEqual(result, d.Expected)
		if !test_ok {
			t.Fail()
		}

		clr := func() *color.Color {
			if test_ok {
				return green
			}
			return red
		}()

		if !test_ok || testing.Verbose() {
			clr.EnableColor() // this is required as go test does shenanigans with colored output
			fmt.Fprintln(t.Output(),
				clr.Sprintf("[%s] (%#v, %#v) -> %#v, expected: %#v",
					isOKStr(result, d.Expected), d.Input1, d.Input2, result, d.Expected))
			clr.DisableColor()
		}
	}
}
