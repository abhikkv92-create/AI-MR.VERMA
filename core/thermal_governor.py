
import logging
import threading
import time

import psutil

log = logging.getLogger("Kernel.Thermal")

class ThermalGovernor:
    """
    Intelligent hardware governor for Intel i9-13900H.
    Directly monitors P-core vs E-core load signatures and calculates 
    a 'Swarm Throttling Factor' (STF) based on thermal simulation.
    """
    def __init__(self, throttle_threshold=85):
        self.throttle_threshold = throttle_threshold
        self.is_throttled = False
        self.current_load = 0
        self.p_core_load = 0
        self.e_core_load = 0
        self._stop_event = threading.Event()
        self._monitor_thread = None

    def start(self):
        """Start the background thermal monitor."""
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        log.info("ThermalGovernor ACTIVE: Monitoring i9-13900H P/E signatures.")

    def stop(self):
        self._stop_event.set()

    def _monitor_loop(self):
        while not self._stop_event.is_set():
            cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
            self.current_load = sum(cpu_per_core) / len(cpu_per_core)

            # i9-13900H: Cores 0-11 are P-core threads, 12-19 are E-cores
            if len(cpu_per_core) >= 20:
                self.p_core_load = sum(cpu_per_core[:12]) / 12
                self.e_core_load = sum(cpu_per_core[12:20]) / 8

            # Simulated Thermal Logic (as sensor access varies on Windows)
            # High P-core load correlated with higher thermal intensity
            simulated_temp = 35 + (self.p_core_load * 0.5) + (self.e_core_load * 0.2)

            if simulated_temp > self.throttle_threshold:
                if not self.is_throttled:
                    log.warning(f"CRITICAL: Simulated Temp {simulated_temp:.1f}C exceeds threshold! THROTTLING Swarm.")
                    self.is_throttled = True
            else:
                if self.is_throttled and simulated_temp < (self.throttle_threshold - 5):
                    log.info(f"NORMAL: Simulated Temp {simulated_temp:.1f}C stabilized. Releasing Throttling.")
                    self.is_throttled = False

            time.sleep(2)

    def get_status(self):
        """Get current thermal and load status for Dashboard integration."""
        return {
            "p_core_load": round(self.p_core_load, 1),
            "e_core_load": round(self.e_core_load, 1),
            "is_throttled": self.is_throttled,
            "sim_temp_c": round(35 + (self.p_core_load * 0.5) + (self.e_core_load * 0.2), 1)
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    gov = ThermalGovernor(throttle_threshold=70) # Lower for demo
    gov.start()
    try:
        while True:
            print(f"Status: {gov.get_status()}")
            time.sleep(5)
    except KeyboardInterrupt:
        gov.stop()
