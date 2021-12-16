from typing import List
from db_connection import SQL
import pickle


class Node:
    def __init__(self, data: chr, end_point: bool):
        self.data = data
        self.next: List[Node] = []
        self.end_point = end_point

    def __str__(self):
        return self.data

    __repr__ = __str__


class Search:
    def __init__(self, usernames):
        self.sql = SQL()
        self.head_node = Node(None, False)
        self._set_search_tree(usernames)
        # self.set_search_tree(self.sql.get_all_usernames()) TODO

    def get_results(self, username_path: str, buffer: int) -> List[str]:
        """
        NOT case sensitive!
        :param username_path:
        :param buffer:
        :return:
        """
        return self._get_results_by_node(username_path.lower(), 0, buffer, self.head_node)

    def _get_results_by_node(self, username_path: str, from_index: int, buffer: int, node: Node) -> List[str]:
        if not node.next:
            return []

        if from_index < len(username_path):
            for current_node in node.next:
                if username_path[from_index] == current_node.data:
                    return self._get_results_by_node(username_path, from_index + 1, buffer, current_node)
        return self._get_results_by_buffer(node, buffer, username_path[:-1], [])

    def _get_results_by_buffer(self, node: Node, buffer: int, username_path: str, usernames: List[str]) -> List[str]:
        """
        TODO
        :param node:
        :param buffer:
        :param username_path:
        :param usernames:
        """
        # root to left to right

        if buffer <= 0:
            return usernames

        username_path += node.data
        if node.end_point:
            usernames.append(username_path)

        if node.next:

            # recursion
            for current_node in node.next:
                current_buffer = len(usernames)
                new_usernames = self._get_results_by_buffer(current_node, buffer, username_path, usernames)
                buffer -= len(new_usernames) - current_buffer

                if buffer <= 0:
                    break

        return usernames

    def _set_search_tree(self, usernames: List[str]):
        list(map(self._insert_to_tree, usernames))

    def _insert_to_tree(self, username: str):
        self._insert_by_node(username.lower(), self.head_node)

    def _insert_by_node(self, username, node):
        if node.next and username:
            for current_node in node.next:
                if username[0] == current_node.data:
                    return self._insert_by_node(username[1:], current_node)

        self._push_to_node(username, node)

    def _push_to_node(self, username, node):
        # just directly
        if username:
            new_node = Node(username[0], True if len(username) == 1 else False)
            node.next.append(new_node)
            self._push_to_node(username[1:], new_node)


def main():
    with open("names_list", "rb") as f:
        l = pickle.loads(f.read())

    s = Search(l)
    print(s.get_results("J", 15))


if __name__ == '__main__':
    main()
