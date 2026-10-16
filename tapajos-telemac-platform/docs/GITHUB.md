# GitHub

Destino: repositório privado [Marcoabo1109/IC](https://github.com/Marcoabo1109/IC), pasta `telemac_workspace/tapajos-telemac-platform`. O conteúdo anterior de IC é preservado. A plataforma local tem seu próprio histórico Git; para contribuir no repositório publicado, use um clone de IC:

```bash
git clone --recurse-submodules https://github.com/Marcoabo1109/IC.git
cd IC/telemac_workspace/tapajos-telemac-platform
./scripts/start.sh
```

A `.gitmodules` na raiz de IC aponta para o TELEMAC fixado em v8p5r0; a cópia dentro da plataforma documenta a estrutura independente. Workflows na raiz de IC usam o subdiretório da plataforma. Imagens Docker e dependências não são armazenadas no Git: as receitas permitem reconstruí-las.

Código, modelos de exemplo, fontes dos dados adquiridos, hipóteses e resultados compactos integram a publicação. Credenciais, ambientes virtuais, node_modules e diretórios temporários de execução são excluídos. Os livros/PDFs locais serviram como referência; a publicação inclui sua proveniência, não cópias indiscriminadas das pastas do dispositivo.
