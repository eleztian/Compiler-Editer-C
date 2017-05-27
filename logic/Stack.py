class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items += item

    def pop(self, num=1):
        t = ''
        for i in range(num):
            t += str(self.items.pop())
        return t

    def clear(self):
        del self.items[:]

    def empty(self):
        return self.size() == 0

    def size(self):
        return len(self.items)

    def top(self):
        return self.items[self.size()-1]
