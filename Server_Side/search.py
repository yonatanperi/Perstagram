from typing import List


class _Node:
    def __init__(self, data: chr, end_point: bool):
        """
        A non-binary tree.
        Every node has list of nexts.
        :param data: the char value the node holds
        :param end_point: whether the node is an end of a letters' path (username is our case)
        """
        self.data: chr = data
        self.next: List[_Node] = []
        self.end_point: bool = end_point

    def __str__(self):
        return self.data

    __repr__ = __str__


class Search:
    def __init__(self, usernames: List[str]):
        """
        Create a search tree and initializing it with the usernames list
        :param usernames: the complete search path's.
        """
        self.head_node = _Node(None, False)
        list(map(self.insert_to_tree, usernames))  # set the search tree

    def get_results(self, username_path: str, buffer: int) -> List[str]:
        """
        Search for the username path in the tree.
        NOT case sensitive!
        :param username_path: the current search path.
        :param buffer: a buffer to the size of the returned list.
        :return: a list of all the matches of the username path.
        """
        return self._get_results_by_node(username_path.lower(), "", buffer, self.head_node)

    def _get_results_by_node(self, username_path: str, current_path: str, buffer: int, node: _Node) -> List[str]:
        """
        Matches the username path is the tree and then calls self._get_results_by_buffer
        :param username_path: the current search path.
        :param current_path: on tree, starts empty.
        :param buffer: a buffer to the size of the returned list.
        :param node: current node (for the recursion)
        :return: a list of all the matches of the username path.
        """
        if len(current_path) < len(username_path):
            for current_node in node.next:
                if username_path[len(current_path)] == current_node.data:
                    return self._get_results_by_node(username_path,
                                                     current_path + username_path[len(current_path)],
                                                     buffer,
                                                     current_node)
            return []

        return self._get_results_by_buffer(node, buffer, current_path[:-1], [])

    def _get_results_by_buffer(self, node: _Node, buffer: int, username_path: str, usernames: List[str]) -> List[str]:
        """
        After the matching of the username path in tree, this func fetch the rest of the path's.
        :param node: current node (for the recursion)
        :param buffer: a buffer to the size of the returned list.
        :param username_path: the current search path.
        :param usernames: the returned list. Starts empty!
        :return: a list of all the matches of the username path.
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

    def insert_to_tree(self, username: str):
        """
        Calls self._insert_by_node with the head node.
        :param username: the usernames.
        """
        self._insert_by_node(username.lower(), self.head_node)

    def _insert_by_node(self, username: str, node: _Node):
        """
        Matches the username string path with the current tree and pushes the remainder path.
        :param username: the string path which gets inserted.
        :param node: current node.
        """
        if node.next and username:
            for current_node in node.next:
                if username[0] == current_node.data:
                    return self._insert_by_node(username[1:], current_node)

        self._push_to_node(username, node)

    def _push_to_node(self, username: str, node: _Node):
        """
        Like linked-list
        :param username: the string path which gets inserted.
        :param node: current node.
        """
        # just directly
        if username:
            new_node = _Node(username[0], True if len(username) == 1 else False)
            node.next.append(new_node)
            self._push_to_node(username[1:], new_node)
