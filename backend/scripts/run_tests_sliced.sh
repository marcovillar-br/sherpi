#!/usr/bin/env bash
# Roda a suíte de testes FATIADA por domínio — cada domínio em um processo pytest
# separado, para que a memória seja liberada entre as fatias e uma fatia pesada não
# derrube a sessão (problema observado no WSL ao rodar tudo de uma vez).
#
# Cada fatia tem guarda de wall-clock (SLICE_TIMEOUT, padrão 180s); somada ao timeout
# POR TESTE do pytest-timeout (pyproject), nenhuma execução pendura indefinidamente.
#
# Uso:
#   scripts/run_tests_sliced.sh                 # todas as fatias (tests/*/)
#   scripts/run_tests_sliced.sh taxonomy api    # apenas estes domínios
#   SLICE_TIMEOUT=300 scripts/run_tests_sliced.sh
set -uo pipefail
cd "$(dirname "$0")/.." || exit 2  # → backend/

SLICE_TIMEOUT="${SLICE_TIMEOUT:-180}"

if [ "$#" -gt 0 ]; then
  slices=()
  for name in "$@"; do slices+=("tests/${name}"); done
else
  slices=()
  for dir in tests/*/; do
    [ "$dir" = "tests/__pycache__/" ] && continue
    slices+=("${dir%/}")
  done
fi

failed=()
for dir in "${slices[@]}"; do
  name="${dir#tests/}"
  if [ ! -d "$dir" ]; then
    echo "== fatia: ${name} — INEXISTENTE, pulada =="
    continue
  fi
  echo "== fatia: ${name} (timeout ${SLICE_TIMEOUT}s) =="
  if ! timeout "${SLICE_TIMEOUT}" uv run pytest "$dir" -q; then
    failed+=("${name}")  # cobre falha de teste E estouro de timeout (124)
  fi
done

echo
if [ "${#failed[@]}" -gt 0 ]; then
  echo "FATIAS COM FALHA/TIMEOUT: ${failed[*]}"
  exit 1
fi
echo "OK — todas as fatias passaram."
