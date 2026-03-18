
class Node:
    def __init__(self, data: dict):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self._size = 0

    def insert(self, data: dict) -> None:
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self._size += 1

    def delete(self, student_id: int) -> bool:
        current = self.head
        previous = None

        while current:
            if current.data.get("student_id") == student_id:
                if previous:
                    previous.next = current.next
                else:
                    self.head = current.next
                self._size -= 1
                return True
            previous = current
            current = current.next

        return False


    def search(self, value, field: str = "student_id") -> dict | None:
        current = self.head
        while current:
            if current.data.get(field) == value:
                return current.data
            current = current.next
        return None


    def traverse(self) -> list[dict]:
        records = []
        current = self.head
        while current:
            records.append(current.data)
            current = current.next
        return records


    def sort(self, key: str = "last_name", reverse: bool = False) -> None:
        self.head = self._merge_sort(self.head, key, reverse)

    def _merge_sort(self, head: Node, key: str, reverse: bool) -> Node:
        if head is None or head.next is None:
            return head

        left, right = self._split(head)
        left  = self._merge_sort(left,  key, reverse)
        right = self._merge_sort(right, key, reverse)
        return self._merge(left, right, key, reverse)

    def _split(self, head: Node) -> tuple[Node, Node]:
        slow = head
        fast = head.next

        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next

        mid = slow.next
        slow.next = None
        return head, mid

    def _merge(self, left: Node, right: Node, key: str, reverse: bool) -> Node:
        dummy = Node({})
        current = dummy

        while left and right:
            left_val  = self._sort_key(left.data,  key)
            right_val = self._sort_key(right.data, key)

            take_left = (left_val <= right_val) if not reverse else (left_val >= right_val)

            if take_left:
                current.next = left
                left = left.next
            else:
                current.next = right
                right = right.next

            current = current.next

        current.next = left if left else right
        return dummy.next

    @staticmethod
    def _sort_key(record: dict, key: str):
        value = record.get(key, "")
        if isinstance(value, str):
            return value.lower()
        return value if value is not None else 0


    def size(self) -> int:
        return self._size


class HashTable:

    DEFAULT_CAPACITY = 64

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        self._capacity = capacity
        self._buckets: list[list] = [[] for _ in range(self._capacity)]
        self._size = 0


    def _hash(self, key: str) -> int:
        hash_value = 0
        base = 31
        for char in key:
            hash_value = (hash_value * base + ord(char)) % self._capacity
        return hash_value


    def put(self, email: str, value: dict) -> None:
        index = self._hash(email)
        bucket = self._buckets[index]

        for i, (k, v) in enumerate(bucket):
            if k == email:
                bucket[i] = (email, value)
                return

        bucket.append((email, value))
        self._size += 1


    def get(self, email: str) -> dict | None:
        index = self._hash(email)
        bucket = self._buckets[index]

        for k, v in bucket:
            if k == email:
                return v

        return None


    def delete(self, email: str) -> bool:
        index = self._hash(email)
        bucket = self._buckets[index]

        for i, (k, v) in enumerate(bucket):
            if k == email:
                bucket.pop(i)
                self._size -= 1
                return True

        return False


    def size(self) -> int:
        return self._size