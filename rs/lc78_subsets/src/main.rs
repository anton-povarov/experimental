// most likely: https://neetcode.io/problems/subsets/question
// also LC-78: https://leetcode.com/problems/subsets/

#![allow(unused)]

// return all possible subsets of a set of unique integers
fn subsets(nums: Vec<i32>) -> Vec<Vec<i32>> {
    subsets_with_bits_imperative(nums)
    // subsets_with_bits(nums)
    // subsets_with_recursion(nums)
}

fn subsets_with_recursion(nums: Vec<i32>) -> Vec<Vec<i32>> {
    fn recursive(nums: &[i32]) -> Vec<Vec<i32>> {
        let mut result = vec![];
        if nums.is_empty() {
            return vec![vec![]];
        }
        for v in recursive(&nums[1..]) {
            result.push([vec![nums[0]], v.clone()].concat());
            result.push(v);
        }
        result
    }
    recursive(&nums[..])
}

fn subsets_with_bits_imperative(nums: Vec<i32>) -> Vec<Vec<i32>> {
    let mut result = Vec::with_capacity(1 << nums.len());

    for subset_id in 0..(1 << nums.len()) {
        let mut subset = Vec::with_capacity(nums.len());
        for i in 0..nums.len() {
            if subset_id & (1 << i) != 0 {
                subset.push(nums[i]);
            }
        }
        result.push(subset);
    }

    return result;
}

fn subsets_with_bits_functional(nums: Vec<i32>) -> Vec<Vec<i32>> {
    let mut result = Vec::with_capacity(1 << nums.len());

    for subset_id in 0..(1 << nums.len()) {
        let subset: Vec<i32> = nums
            .iter()
            .enumerate()
            .filter_map(|(i, &num)| {
                if (subset_id & (1 << i)) != 0 {
                    Some(num)
                } else {
                    None
                }
            })
            .collect();

        result.push(subset);
    }

    return result;
}

fn main() {
    println!("{:?}", subsets(vec![1, 2, 3]));
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty_set() {
        let result = subsets(vec![]);
        let expected = vec![vec![]];
        println!("r: {:?}, e: {:?}", result, expected);
        assert_eq!(result, expected);
    }

    #[test]
    fn test_single_element() {
        let result = subsets(vec![1]);
        let expected = vec![vec![], vec![1]];
        println!("r: {:?}, e: {:?}", result, expected);
        // Sort for consistent comparison
        result.iter().for_each(|v| assert!(expected.contains(v)));
        assert_eq!(result.len(), expected.len());
    }

    #[test]
    fn test_two_elements() {
        let result = subsets(vec![1, 2]);
        let expected = vec![vec![], vec![1], vec![2], vec![1, 2]];
        println!("r: {:?}, e: {:?}", result, expected);
        // Ensure all expected subsets are present
        result.iter().for_each(|v| assert!(expected.contains(v)));
        assert_eq!(result.len(), expected.len());
    }

    #[test]
    fn test_three_elements() {
        let result = subsets(vec![1, 2, 3]);
        let expected = vec![
            vec![],
            vec![1],
            vec![2],
            vec![1, 2],
            vec![3],
            vec![1, 3],
            vec![2, 3],
            vec![1, 2, 3],
        ];
        println!("r: {:?}, e: {:?}", result, expected);
        // Ensure all expected subsets are present
        result.iter().for_each(|v| assert!(expected.contains(v)));
        assert_eq!(result.len(), expected.len());
    }

    #[test]
    fn test_result_count() {
        // For n elements, there should be 2^n subsets
        let nums = vec![1, 2, 3, 4];
        let result = subsets(nums.clone());
        assert_eq!(result.len(), 1 << nums.len());
    }

    #[test]
    fn test_negative_numbers() {
        let result = subsets(vec![-1, -2]);
        let expected = vec![vec![], vec![-1], vec![-2], vec![-1, -2]];
        result.iter().for_each(|v| assert!(expected.contains(v)));
        assert_eq!(result.len(), expected.len());
    }
}
