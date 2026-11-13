
class Job:
    def __init__(self, name, priority, submitted):
        self.name = name
        self.priority = priority
        self.submitted = submitted

    def __lt__(self, other):
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.submitted < other.submitted


def parent(i):
    return (i - 1) // 2


def left(i):
    return 2 * i + 1


def right(i):
    return 2 * i + 2


class GPUQueue:
    def __init__(self):
        self.h = []

    def sift_up(self, i):
        while i > 0 and self.h[i] < self.h[parent(i)]:
            p = parent(i)
            self.h[i], self.h[p] = self.h[p], self.h[i]
            i = p

    def sift_down(self, i):
        n = len(self.h)
        while left(i) < n:
            c = left(i)
            if right(i) < n and self.h[right(i)] < self.h[c]:
                c = right(i)
            if self.h[c] < self.h[i]:
                self.h[i], self.h[c] = self.h[c], self.h[i]
                i = c
            else:
                break

    def submit(self, job):
        self.h.append(job)
        self.sift_up(len(self.h) - 1)

    def next_job(self):
        if len(self.h) == 0:
            return None
        top = self.h[0]
        last = self.h.pop()
        if len(self.h) > 0:
            self.h[0] = last
            self.sift_down(0)
        return top

    def cancel(self, name):
        for i in range(len(self.h)):
            if self.h[i].name == name:
                last = self.h.pop()
                if i < len(self.h):
                    self.h[i] = last
                    if i > 0 and self.h[i] < self.h[parent(i)]:
                        self.sift_up(i)
                    else:
                        self.sift_down(i)
                return True
        return False


def main():
    q = GPUQueue()
    n = int(input())
    submitted = 0
    for _ in range(n):
        parts = input().split()
        if parts[0] == "SUBMIT":
            submitted += 1
            q.submit(Job(parts[1], int(parts[2]), submitted))
        elif parts[0] == "RUN":
            job = q.next_job()
            if job is None:
                print("GPU idle")
            else:
                print(job.name)
        elif parts[0] == "CANCEL":
            if not q.cancel(parts[1]):
                print(parts[1], "not found")


main()


# EXPLANATION OF BUG FIXES:

# 1. Changed the submission comparison from > to < in __lt__()
# so that jobs with equal priority run in the order they were submitted.

# 2. Changed / to // in the parent() function because
# heap indexes must be integer values.

# 3. Added the missing colon (:) in the cancel() function
# definition to correct the syntax error.

# 4. Corrected the comparison in sift_down() to select
# the smaller child while maintaining the min-heap property.

# 5. Modified next_job() to handle the case when the heap
# contains only one job, preventing unnecessary heap repair
# after removing the last element.

# 6. Modified cancel() to check the correct repair direction.
# If the replacement job is smaller than its parent, sift_up()
# is performed; otherwise, sift_down() is performed.
