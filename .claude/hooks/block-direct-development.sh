#!/usr/bin/env bash
# PreToolUse (Bash) — barra commit/push direto na branch protegida 'development'.
# A entrega deve ir por feature-branch → PR para development (ver CONTRIBUTING.md, "Fluxo de Git").
# Saída 2 = bloqueia a chamada e devolve a mensagem (stderr) ao agente.
#
# Precisão: só inspeciona SEGMENTOS de comando que COMEÇAM com `git push`/`git commit`
# (separados por && || ; | e quebras de linha). Assim, `git push`/`development` que apareçam
# como argumento ou dentro de uma mensagem de commit (heredoc) NÃO disparam falso-positivo.
set -euo pipefail

cmd=$(cat | jq -r '.tool_input.command // ""')
case "$cmd" in
  *git*) ;;
  *) exit 0 ;;  # não é comando git — ignora
esac

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

deny() {
  echo "BLOQUEADO: $1" >&2
  echo "Regra do projeto: nunca commit/push direto na 'development'. Crie um feature-branch e abra PR para development (CONTRIBUTING.md → Fluxo de Git)." >&2
  exit 2
}

# Quebra o comando em segmentos por separadores de shell (&& || ; |) e por linhas.
segments=$(printf '%s' "$cmd" | sed -E 's/(\&\&|\|\||;|\|)/\n/g')

while IFS= read -r seg; do
  [ -z "$seg" ] && continue

  # push: segmento que começa com `git push`
  if printf '%s' "$seg" | grep -qiE '^[[:space:]]*(sudo[[:space:]]+)?git[[:space:]]+push([[:space:]]|$)'; then
    # alvo explícito = development
    if printf '%s' "$seg" | grep -qiE '(^|[[:space:]:])development([[:space:]:]|$)'; then
      deny "push para a branch 'development'."
    fi
    # push 'pelado' (sem refspec de outra branch) estando em development
    if [ "$branch" = "development" ] && \
       printf '%s' "$seg" | grep -qiE '^[[:space:]]*(sudo[[:space:]]+)?git[[:space:]]+push([[:space:]]+(-u|--set-upstream))?([[:space:]]+origin)?([[:space:]]+HEAD)?[[:space:]]*$'; then
      deny "push da branch atual (development) para o remoto."
    fi
  fi

  # commit: segmento que começa com `git commit`, estando em development
  if [ "$branch" = "development" ] && \
     printf '%s' "$seg" | grep -qiE '^[[:space:]]*(sudo[[:space:]]+)?git[[:space:]]+commit([[:space:]]|$)'; then
    deny "commit na branch 'development'."
  fi
done <<EOF
$segments
EOF

exit 0
