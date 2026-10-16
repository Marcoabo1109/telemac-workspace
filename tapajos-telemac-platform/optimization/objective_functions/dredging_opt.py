import numpy as np


class DredgingObjective:
    def evaluate(
        self,
        h_field: np.ndarray,
        u_field: np.ndarray,
        v_field: np.ndarray,
        C_field: np.ndarray,
        dredge_params: dict,
    ) -> float:
        """Interface reservada à definição científica pelos professores."""
        raise NotImplementedError(
            "Definir objetivo, unidades, domínio e restrições com a equipe científica"
        )
