# logic/analyzer/scheduler.py
from __future__ import annotations
import time
from typing import Optional
from config import TPM_BUDGET, RPM_BUDGET, COOLDOWN_MS


class RateLimiter:
    """
    Limitador simple por ventana deslizante de 60s para tokens y requests.
    """
    def __init__(self, tpm_budget: int = TPM_BUDGET, rpm_budget: int = RPM_BUDGET, cooldown_ms: int = COOLDOWN_MS):
        self.tpm = tpm_budget
        self.rpm = rpm_budget
        self.cooldown_ms = cooldown_ms

        self._win_start = time.time()
        self._tokens_used = 0
        self._reqs_used = 0

    def _rollover(self):
        now = time.time()
        if now - self._win_start >= 60.0:
            self._win_start = now
            self._tokens_used = 0
            self._reqs_used = 0

    def allow(self, tokens_needed: int):
        """
        Bloquea hasta que haya presupuesto suficiente para consumir tokens_needed y 1 request.
        """
        while True:
            self._rollover()
            if (self._tokens_used + tokens_needed <= self.tpm) and (self._reqs_used + 1 <= self.rpm):
                self._tokens_used += tokens_needed
                self._reqs_used += 1
                if self.cooldown_ms > 0:
                    time.sleep(self.cooldown_ms / 1000.0)
                return
            # dormir hasta siguiente ventana (o hasta liberar tokens)
            to_wait = max(0.1, 60.0 - (time.time() - self._win_start))
            time.sleep(min(2.0, to_wait))
