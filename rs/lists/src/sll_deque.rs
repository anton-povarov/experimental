#![cfg(test)]

use std::ptr;

struct Node<T> {
    elem: T,
    next: *mut Node<T>,
}

pub struct List<T> {
    head: *mut Node<T>,
    tail: *mut Node<T>,
}

impl<T> List<T> {
    pub fn new() -> Self {
        List {
            head: ptr::null_mut(),
            tail: ptr::null_mut(),
        }
    }

    pub fn push_back(&mut self, elem: T) {
        let new_node = Box::into_raw(Box::new(Node {
            elem: elem,
            next: ptr::null_mut(),
        }));

        if self.tail.is_null() {
            // empty list
            self.tail = new_node;
            self.head = new_node;
        } else {
            // link after tail
            unsafe {
                (*self.tail).next = new_node;
            }
            self.tail = new_node;
        }
    }

    pub fn pop_front(&mut self) -> Option<T> {
        unsafe {
            if self.head.is_null() {
                return None;
            }

            let head = Box::from_raw(self.head);
            if head.next.is_null() {
                self.tail = ptr::null_mut();
            }
            self.head = head.next;
            Some(head.elem)
        }
    }

    pub fn peek_front(&self) -> Option<&T> {
        unsafe { self.head.as_ref().map(|node| &node.elem) }
    }

    pub fn peek_front_mut(&mut self) -> Option<&mut T> {
        unsafe { self.head.as_mut().map(|node| &mut node.elem) }
    }

    pub fn into_iter(self) -> IntoIter<T> {
        IntoIter { list: self }
    }

    pub fn iter(&self) -> Iter<'_, T> {
        Iter {
            node: unsafe { self.head.as_ref() },
        }
    }
    pub fn iter_mut(&mut self) -> IterMut<'_, T> {
        IterMut {
            node: unsafe { self.head.as_mut() },
        }
    }
}

impl<T> Drop for List<T> {
    fn drop(&mut self) {
        while let Some(_) = self.pop_front() {}
    }
}

pub struct IntoIter<T> {
    list: List<T>,
}

impl<T> Iterator for IntoIter<T> {
    type Item = T;
    fn next(&mut self) -> Option<Self::Item> {
        self.list.pop_front()
    }
}

pub struct Iter<'a, T> {
    node: Option<&'a Node<T>>,
}

impl<'a, T> Iterator for Iter<'a, T> {
    type Item = &'a T;

    fn next(&mut self) -> Option<Self::Item> {
        unsafe {
            self.node.take().map(|node| {
                self.node = node.next.as_ref();
                &node.elem
            })
        }
    }
}

pub struct IterMut<'a, T> {
    node: Option<&'a mut Node<T>>,
}

impl<'a, T> Iterator for IterMut<'a, T> {
    type Item = &'a mut T;

    fn next(&mut self) -> Option<Self::Item> {
        unsafe {
            self.node.take().map(|node| {
                self.node = node.next.as_mut();
                &mut node.elem
            })
        }
    }
}

// ------------------------------------------------------------------------------------------------

#[cfg(test)]
mod test {
    use super::List;
    use std::{cell::RefCell, rc::Rc};

    struct VerboseDrop {
        dtor_trace: Rc<RefCell<Vec<u32>>>,
        v: u32,
    }

    impl VerboseDrop {
        fn new(v: u32, trace: Rc<RefCell<Vec<u32>>>) -> Self {
            VerboseDrop {
                dtor_trace: trace,
                v: v,
            }
        }
    }

    impl Drop for VerboseDrop {
        fn drop(&mut self) {
            println!("{:p} v = {} is dropped", self as *mut _, self.v);
            self.dtor_trace.borrow_mut().push(self.v);
        }
    }

    #[test]
    fn basics() {
        let mut list = List::<u32>::new();
        list.push_back(1);
        list.push_back(2);

        assert_eq!(list.pop_front(), Some(1));
        assert_eq!(list.pop_front(), Some(2));
        assert_eq!(list.pop_front(), None);
        assert_eq!(list.pop_front(), None);

        list.push_back(3);
        list.push_back(4);
        assert_eq!(list.pop_front(), Some(3));
        assert_eq!(list.pop_front(), Some(4));
        assert_eq!(list.pop_front(), None);
    }

    #[test]
    fn drop_destructor_order() {
        let dtor_trace = Rc::new(RefCell::new(vec![]));
        {
            let mut list = List::new();
            list.push_back(VerboseDrop::new(1, dtor_trace.clone()));
            list.push_back(VerboseDrop::new(2, dtor_trace.clone()));
            list.push_back(VerboseDrop::new(3, dtor_trace.clone()));
        }
        assert_eq!(vec![1, 2, 3], *dtor_trace.borrow());
    }

    #[test]
    fn into_iter_full() {
        let mut list = List::<u32>::new();
        list.push_back(1);
        list.push_back(2);
        list.push_back(5);

        let values = list.into_iter().collect::<Vec<_>>();
        assert_eq!(values, vec![1, 2, 5]);
    }

    #[test]
    fn const_iter() {
        let mut list = List::new();
        list.push_back(1);
        list.push_back(2);
        list.push_back(5);

        let values = list.iter().map(|v| *v).collect::<Vec<_>>();
        assert_eq!(values, vec![1, 2, 5]);
    }

    #[test]
    fn mutable_iter() {
        let mut list = List::new();
        list.push_back(1);
        list.push_back(2);
        list.push_back(5);

        let values = list.iter_mut().map(|v| *v).collect::<Vec<_>>();
        assert_eq!(values, vec![1, 2, 5]);

        let mut refs = list.iter_mut().collect::<Vec<_>>();
        (*refs[1]) = -300;

        let values = list.iter_mut().map(|v| *v).collect::<Vec<_>>();
        assert_eq!(values, vec![1, -300, 5]);
    }

    #[test]
    fn mutate_for_miri() {
        let mut list = List::new();
        list.push_back(1);
        list.push_back(2);
        list.push_back(5);

        list.peek_front_mut().map(|x| (*x) *= 10);
        assert_eq!(list.peek_front(), Some(&10));
        assert_eq!(list.peek_front().unwrap(), &10);
        assert_eq!(*list.peek_front().unwrap(), 10);

        let mut it = list.iter_mut();
        it.next().map(|x| (*x) += 50);

        assert_eq!(list.peek_front(), Some(&60));
    }
}
