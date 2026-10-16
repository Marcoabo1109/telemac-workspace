# Consolidação

`manifest.json` registra caminho original, caminho publicado, tamanho original e SHA-256 de cada arquivo incluído. Arquivos maiores que 50 MiB são publicados em gzip; se necessário, o gzip é dividido em partes de até 48 MiB. `restore_large_files.py` recompõe os originais sem excluir os arquivos publicados.

`excluded.json` lista ambientes instalados, metadados Git, caches e arquivos do macOS excluídos. Os arquivos `.gitmodules` foram removidos da cópia porque os conteúdos presentes são incorporados como arquivos comuns. Os históricos dos repositórios aninhados não são fundidos: a publicação é um snapshot dos arquivos atuais. `provenance.json` registra os commits de origem disponíveis.

As cópias `IC-official` e `tapajos-telemac-platform` permanecem distintas. Não houve escolha silenciosa de uma versão sobre outra. O Git compartilha armazenamento para conteúdos idênticos.

A pasta `entrega_caso_tapajos` continha apenas `.DS_Store`; não havia entrega científica a incluir nela. `github-publication.json` na raiz é um registro histórico da publicação anterior em `Marcoabo1109/IC`.

Os originais em `/Users/marcoabo/telemac_workspace` não foram movidos nem alterados. Esta cópia foi preparada em `publication/telemac-workspace`.

As regras `.gitattributes` de origem foram preservadas como `.gitattributes.upstream`; regras novas desativam filtros LFS e conversão de texto, para armazenar os bytes diretamente. O inventário registra esses caminhos de publicação.
