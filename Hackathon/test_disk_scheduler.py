import unittest
from disk_scheduler import run_all

Q = [98, 183, 37, 122, 14, 124, 65, 67]


class TestDiskScheduling(unittest.TestCase):
    def totals(self, *a, **k):
        return {r["name"]: r["total"] for r in run_all(*a, **k)}

    def test_textbook_up(self):
        t = self.totals(53, Q, 200, "up")
        self.assertEqual(t, {"FCFS": 640, "SSTF": 236, "SCAN": 331, "C-SCAN": 382})

    def test_cscan_without_jump(self):
        self.assertEqual(self.totals(53, Q, 200, "up", False)["C-SCAN"], 183)

    def test_scan_down(self):
        self.assertEqual(self.totals(53, Q, 200, "down")["SCAN"], 53 + 183)

    def test_single_request(self):
        t = self.totals(10, [10], 100)
        self.assertTrue(all(v == 0 for v in t.values()))

    def test_head_at_zero(self):
        t = self.totals(0, [5, 10, 20], 50, "up")
        self.assertEqual(t["SCAN"], 20)

    def test_all_requests_served(self):
        for r in run_all(53, Q, 200, "up"):
            served = [c for c, j in r["path"][1:] if not j]
            for q in Q:
                self.assertIn(q, served)

    def test_duplicates(self):
        t = self.totals(50, [50, 50, 70], 100)
        self.assertEqual(t["FCFS"], 20)


if __name__ == "__main__":
    unittest.main()
