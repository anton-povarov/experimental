use std::collections::HashMap;

#[allow(dead_code)]
#[derive(Debug)]
struct Point<T> {
    x: T,
    y: T,
}

fn main() {
    print!("hello world {1} {0}\n", 10, get_me_a_string("abc"));

    let mut h = HashMap::new();
    h.insert("Alice", 1);
    h.insert("Bob", 2);
    println!("h: {}\n{:#?}", std::any::type_name_of_val(&h), h)
}

fn get_me_a_string(prefix: &str) -> String {
    // return "'Hello'".into();
    format!(
        "'some other string + {} + {:?}'",
        prefix,
        Point { x: 1, y: 2 }
    )
}
