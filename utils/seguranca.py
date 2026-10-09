"""
Utilitários de segurança (sem dependência do Flask):
hash de senha e limitador de tentativas de login.
"""

import threading
import time
from collections import defaultdict, deque

from werkzeug.security import check_password_hash, generate_password_hash

# pbkdf2:sha256 funciona em qualquer instalação do Python (scrypt depende do OpenSSL).
_METODO_HASH = "pbkdf2:sha256"

# Hash "falso" usado quando o e-mail não existe, para que o tempo de resposta
# seja parecido com o de um e-mail existente (evita descobrir e-mails cadastrados).
_HASH_FALSO = generate_password_hash("senha-falsa-apenas-para-igualar-tempo", method=_METODO_HASH)


def gerar_hash(senha):
    return generate_password_hash(senha, method=_METODO_HASH)


def conferir_senha(senha, senha_hash):
    """Confere a senha com o hash. Se não houver hash, gasta o mesmo tempo e retorna False."""
    if not senha_hash:
        check_password_hash(_HASH_FALSO, senha)
        return False
    try:
        return check_password_hash(senha_hash, senha)
    except ValueError:
        return False


class LimitadorTentativas:
    """
    Conta falhas por chave (ex.: IP+e-mail). Ao atingir max_falhas dentro da
    janela, bloqueia a chave por um tempo. O bloqueio é temporário.

    Fica em memória: vale para um único processo do servidor. Em produção com
    vários processos, use um armazenamento compartilhado (ex.: Redis).
    """

    def __init__(self, max_falhas, janela_segundos, bloqueio_segundos):
        self.max_falhas = max_falhas
        self.janela = janela_segundos
        self.bloqueio = bloqueio_segundos
        self._falhas = defaultdict(deque)
        self._bloqueado_ate = {}
        self._lock = threading.Lock()

    def segundos_bloqueado(self, chave):
        """Segundos restantes de bloqueio (0 se a chave não está bloqueada)."""
        agora = time.monotonic()
        with self._lock:
            ate = self._bloqueado_ate.get(chave)
            if ate is None:
                return 0
            if ate > agora:
                return int(ate - agora) + 1
            del self._bloqueado_ate[chave]
            return 0

    def registrar_falha(self, chave):
        agora = time.monotonic()
        with self._lock:
            falhas = self._falhas[chave]
            while falhas and agora - falhas[0] > self.janela:
                falhas.popleft()
            falhas.append(agora)
            if len(falhas) >= self.max_falhas:
                self._bloqueado_ate[chave] = agora + self.bloqueio
                falhas.clear()
            if len(self._falhas) > 10000:
                self._limpar_antigos(agora)

    def limpar(self, chave):
        with self._lock:
            self._falhas.pop(chave, None)
            self._bloqueado_ate.pop(chave, None)

    def _limpar_antigos(self, agora):
        for chave in list(self._falhas):
            falhas = self._falhas[chave]
            while falhas and agora - falhas[0] > self.janela:
                falhas.popleft()
            if not falhas:
                del self._falhas[chave]
        for chave in list(self._bloqueado_ate):
            if self._bloqueado_ate[chave] <= agora:
                del self._bloqueado_ate[chave]
