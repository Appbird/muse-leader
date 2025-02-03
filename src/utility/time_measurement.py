# By ChatGPT gpt-4o-2024-05-13
import time
class Stopwatch:
    def __init__(self):
        self.start_time = None

    def start(self):
        """計測を開始します"""
        self.start_time = time.perf_counter()
    
    def measure(self):
        """経過時間を返します"""
        if self.start_time is None:
            raise ValueError("Stopwatch has not been started. Call start() to start the stopwatch.")
        elapsed_time = time.perf_counter() - self.start_time
        return elapsed_time
