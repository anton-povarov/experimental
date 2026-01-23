#![cfg(test)]

use std::fmt::Debug;
use std::{marker::PhantomData, ptr::NonNull};

struct LinkedList<T> {
    head: Link<T>,
    tail: Link<T>,
    _p: PhantomData<T>,
}

struct Node<T> {
    value: T,
    next: Link<T>,
    prev: Link<T>,
}

type Link<T> = Option<NonNull<Node<T>>>;

impl<T> LinkedList<T> {
    pub fn new() -> Self {
        LinkedList {
            head: None,
            tail: None,
            _p: PhantomData,
        }
    }

    pub fn push_front(&mut self, value: T) {
        unsafe {
            let new_node = NonNull::new_unchecked(Box::into_raw(Box::new(Node {
                value: value,
                next: None,
                prev: None,
            })));

            match self.head {
                Some(head) => {
                    (*new_node.as_ptr()).next = Some(head);
                    (*head.as_ptr()).prev = Some(new_node);
                }
                None => {
                    debug_assert!(self.head.is_none());
                    debug_assert!(self.tail.is_none());
                    self.tail = Some(new_node);
                }
            }

            self.head = Some(new_node);
        }
    }

    pub fn pop_front(&mut self) -> Option<T> {
        unsafe {
            self.head.take().map(|head| {
                let node = Box::from_raw(head.as_ptr());

                self.head = node.next;
                match self.head {
                    Some(new_head) => {
                        (*new_head.as_ptr()).prev = None; // head must have no prev pointer
                    }
                    None => {
                        // list is now empty
                        self.tail = None;
                    }
                }

                node.value
            })
        }
    }

    pub fn push_back(&mut self, value: T) {
        unsafe {
            let new_node = NonNull::new_unchecked(Box::into_raw(Box::new(Node {
                value: value,
                next: None,
                prev: None,
            })));

            match self.tail {
                Some(tail) => {
                    (*new_node.as_ptr()).prev = Some(tail);
                    (*tail.as_ptr()).next = Some(new_node);
                }
                None => {
                    self.head = Some(new_node);
                }
            }

            self.tail = Some(new_node)
        }
    }

    pub fn pop_back(&mut self) -> Option<T> {
        unsafe {
            self.tail.take().map(|tail| {
                let node = Box::from_raw(tail.as_ptr());
                let value = node.value;

                self.tail = node.prev;
                match self.tail {
                    Some(new_tail) => {
                        (*new_tail.as_ptr()).next = None; // tail must not have an end pointer
                    }
                    None => {
                        // empty list
                        self.head = None;
                    }
                }

                value
            })
        }
    }

    pub fn front(&self) -> Option<&T> {
        unsafe {
            self.head.map(|head| &(*head.as_ptr()).value)
            // same as
            //   self.head.map(|head| {
            //       let node = &(*head.as_ptr());
            //       &node.value
            //   })
            // same as
            //   Some(&(*self.head?.as_ptr()).value)
            // same as
            //   if let Some(head) = self.head {
            //       Some(&(*head.as_ptr()).value)
            //   } else {
            //       None
            //   }
            // same as
            // match self.head {
            //     Some(head) => Some(&(*head.as_ptr()).value),
            //     None => None,
            // }
        }
    }

    pub fn front_mut(&mut self) -> Option<&mut T> {
        unsafe { self.head.map(|head| &mut (*head.as_ptr()).value) }
    }

    pub fn back(&self) -> Option<&T> {
        unsafe { self.tail.map(|tail| &(*tail.as_ptr()).value) }
    }

    pub fn back_mut(&mut self) -> Option<&mut T> {
        unsafe { self.tail.map(|tail| &mut (*tail.as_ptr()).value) }
    }

    fn iter(&self) -> Iter<'_, T> {
        self.into_iter()
    }

    fn iter_mut(&mut self) -> IterMut<'_, T> {
        self.into_iter()
    }

    fn is_empty(&self) -> bool {
        self.head.is_none()
    }

    fn clear(&mut self) {
        while let Some(_) = self.pop_front() {}
    }
}

impl<T> Drop for LinkedList<T> {
    fn drop(&mut self) {
        self.clear()
    }
}

impl<T> Default for LinkedList<T> {
    fn default() -> Self {
        Self::new()
    }
}

impl<T: Debug> Debug for LinkedList<T> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_list().entries(self.iter()).finish()
    }
}

impl<T> Extend<T> for LinkedList<T> {
    fn extend<I: IntoIterator<Item = T>>(&mut self, iter: I) {
        for value in iter {
            self.push_back(value);
        }
    }
}

impl<T: Clone> Clone for LinkedList<T> {
    fn clone(&self) -> Self {
        let mut new_list = Self::new();
        for value in self.iter() {
            new_list.push_back(value.clone());
        }
        new_list
    }
}

// ------------------------------------------------------------------------------------------------
// into_iter consume

struct IntoIter<T> {
    list: LinkedList<T>,
}

impl<T> IntoIterator for LinkedList<T> {
    type IntoIter = IntoIter<T>;
    type Item = T;

    fn into_iter(self) -> Self::IntoIter {
        IntoIter { list: self }
    }
}

impl<T> Iterator for IntoIter<T> {
    type Item = T;
    fn next(&mut self) -> Option<Self::Item> {
        self.list.pop_front()
    }
}

impl<T> DoubleEndedIterator for IntoIter<T> {
    fn next_back(&mut self) -> Option<Self::Item> {
        self.list.pop_back()
    }
}

// ------------------------------------------------------------------------------------------------
// iter

struct Iter<'a, T> {
    begin: Option<NonNull<Node<T>>>,
    end: Option<NonNull<Node<T>>>,
    _p: PhantomData<&'a T>,
}

impl<'a, T> Iterator for Iter<'a, T> {
    type Item = &'a T;
    fn next(&mut self) -> Option<Self::Item> {
        unsafe {
            self.begin.map(|node| {
                let value = &(*node.as_ptr()).value;
                self.begin = (*node.as_ptr()).next;
                value
            })
        }
    }
}

impl<'a, T> DoubleEndedIterator for Iter<'a, T> {
    fn next_back(&mut self) -> Option<Self::Item> {
        unsafe {
            self.end.map(|node| {
                self.end = (*node.as_ptr()).prev;
                &(*node.as_ptr()).value
            })
        }
    }
}

impl<'a, T> IntoIterator for &'a LinkedList<T> {
    type IntoIter = Iter<'a, T>;
    type Item = &'a T;

    fn into_iter(self) -> Self::IntoIter {
        Iter {
            begin: self.head,
            end: self.tail,
            _p: PhantomData,
        }
    }
}

// ------------------------------------------------------------------------------------------------
// iter mut

struct IterMut<'a, T> {
    begin: Option<NonNull<Node<T>>>,
    end: Option<NonNull<Node<T>>>,
    _p: PhantomData<&'a T>,
}

impl<'a, T> Iterator for IterMut<'a, T> {
    type Item = &'a mut T;
    fn next(&mut self) -> Option<Self::Item> {
        unsafe {
            self.begin.map(|node| {
                let value = &mut (*node.as_ptr()).value;
                self.begin = (*node.as_ptr()).next;
                value
            })
        }
    }
}

impl<'a, T> DoubleEndedIterator for IterMut<'a, T> {
    fn next_back(&mut self) -> Option<Self::Item> {
        unsafe {
            self.end.map(|node| {
                self.end = (*node.as_ptr()).prev;
                &mut (*node.as_ptr()).value
            })
        }
    }
}

impl<'a, T> IntoIterator for &'a mut LinkedList<T> {
    type IntoIter = IterMut<'a, T>;
    type Item = &'a mut T;

    fn into_iter(self) -> Self::IntoIter {
        IterMut {
            begin: self.head,
            end: self.tail,
            _p: PhantomData,
        }
    }
}

// ------------------------------------------------------------------------------------------------

#[cfg(test)]
mod test {
    use super::LinkedList;

    #[test]
    fn basics() {
        let mut list = LinkedList::new();
        list.push_front(0);
        list.push_back(1);
        list.push_back(2);

        assert_eq!(list.pop_front(), Some(0));
        assert_eq!(list.pop_front(), Some(1));
        assert_eq!(list.pop_front(), Some(2));
        assert_eq!(list.pop_front(), None);
        assert_eq!(list.pop_front(), None);

        list.push_back(3);
        list.push_back(4);
        assert_eq!(list.pop_front(), Some(3));
        assert_eq!(list.pop_front(), Some(4));
        assert_eq!(list.pop_front(), None);

        list.push_back(5);
        list.push_back(6);
        assert_eq!(list.pop_back(), Some(6));
        list.push_back(7);
        assert_eq!(list.pop_back(), Some(7));
        assert_eq!(list.pop_back(), Some(5));
        assert_eq!(list.pop_back(), None);

        list.push_front(10);
        list.push_front(11);
        list.push_back(12);
        assert_eq!(list.pop_front(), Some(11));
        assert_eq!(list.pop_front(), Some(10));
        assert_eq!(list.pop_front(), Some(12));
        assert_eq!(list.pop_front(), None);
        assert_eq!(list.pop_back(), None);
    }

    #[test]
    fn iteration() {
        let mut list = LinkedList::new();
        list.push_front(0);
        list.push_back(1);
        list.push_back(2);

        let values = list.iter().map(|v| v * 2).collect::<Vec<_>>();
        assert_eq!(values, vec![0, 2, 4]);

        list.push_back(10);
        let values = list.iter().map(|v| v * 2).collect::<Vec<_>>();
        assert_eq!(values, vec![0, 2, 4, 20]);

        list.push_back(20);
        for v in &mut list {
            (*v) += -1;
        }

        let values = list.iter().map(|v| *v).collect::<Vec<_>>();
        assert_eq!(values, vec![-1, 0, 1, 9, 19]);

        for v in list.iter_mut().rev() {
            (*v) += 1;
        }

        let values = list.iter().rev().map(|v| *v).collect::<Vec<_>>();
        assert_eq!(values, vec![20, 10, 2, 1, 0]);

        // final consume with .into_iter()
        let values = list.into_iter().collect::<Vec<_>>();
        assert_eq!(values, vec![0, 1, 2, 10, 20]);

        // reverse consume
        {
            let mut list = LinkedList::new();
            for v in values {
                list.push_back(v);
            }
            let values = list.into_iter().rev().collect::<Vec<_>>();
            assert_eq!(values, vec![20, 10, 2, 1, 0]);
        }
    }

    #[test]
    fn debug_print() {
        let mut list = LinkedList::new();
        list.push_front(0);
        list.push_back(-1);
        list.push_back(2);
        list.push_back(-3);
        list.push_back(4);

        println!("{:?}", list);
        println!("{}", list);
    }
}
