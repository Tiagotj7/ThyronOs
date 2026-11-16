# THYRON Store

Primeiro esqueleto técnico da central de aplicativos do THYRON OS.

## Estado desta entrega

- Interface GTK 4 com identidade visual THYRON: primeira atualização visual implementada.
- Descoberta de aplicativos `.desktop`: implementada, incluindo ícone, categorias e nome/descrição em português quando disponíveis.
- Inventário APT/dpkg: consulta somente leitura.
- Inventário Flatpak: consulta somente leitura, se o comando estiver disponível.
- Cartões com ícones, origem e versão; janela de detalhes do aplicativo: implementados nesta etapa.
- Instalar, remover e atualizar: **não implementado** nesta etapa.
- Elevação de privilégios: **não implementada**. Nenhum comando administrativo é executado pela interface.

## Requisitos de desenvolvimento

- Python 3.11+
- GTK 4 com introspecção GObject (`python3-gi`, `gir1.2-gtk-4.0`)
- Opcional: `flatpak` para consultar instalações Flatpak

No Kali, confirme a disponibilidade dos pacotes antes de instalar dependências:
`apt-cache policy python3-gi gir1.2-gtk-4.0 flatpak`

## Executar

A partir da raiz do repositório:

`python3 -m applications.store.thyron_store`

Se o GTK 4 não estiver disponível, a aplicação informa a dependência ausente. Os módulos de catálogo podem ser testados sem GTK.

## Identidade visual

- Logo THYRON Store e banner do lobo incluídos em `thyron_store/assets/`.
- Painel inicial com cartões de estatísticas e atalhos de navegação.
- Navegação, pesquisa e favoritos preservados.

## Próximas etapas

1. Validar ícones e janela de detalhes na VM Kali.
2. Melhorar metadados e deduplicação entre APT/Flatpak e atalhos gráficos.
3. Projetar a camada de operações com autorização via PolicyKit.
4. Só então implementar operações APT/Flatpak e testes em VM descartável.


## Ícone do aplicativo

- Ícone da THYRON Store derivado da marca do lobo: `thyron_store/assets/thyron-store-icon.png`.
- O pacote instala o ícone no tema `hicolor` (48, 128, 256 e 512 px) e o lançador `org.thyron.Store.desktop`.
- O lançador usa `Icon=thyron-store` e `StartupWMClass=org.thyron.Store`, em correspondência com o ID GTK da aplicação.
- O comando instalado é `thyron-store`.
- A janela solicita o ícone nomeado quando o backend GTK disponibiliza esse método. Em ambientes GTK 4 que não expõem ícone por janela, o ambiente gráfico deve associar o ícone pelo arquivo `.desktop` e pelo ID da aplicação.

Após instalar/atualizar o pacote, atualize o cache do tema de ícones se necessário (`gtk-update-icon-cache` quando disponível) e encerre/reabra o aplicativo. A aparência final na barra de título depende do gerenciador de janelas e ainda precisa ser validada na VM Kali.

## Configurações (atualização)

- A aba **Configurações** agora apresenta controles funcionais.
- A opção para exibir/ocultar o aviso de modo de leitura é salva automaticamente em `~/.config/thyron-store/settings.json`.
- O botão **Atualizar catálogo agora** relê os atalhos `.desktop` e os inventários APT/Flatpak, sem executar instalação, remoção ou alteração de pacotes.

## Aba Aplicativos instalados (atualização visual)

- A página apresenta os lançadores gráficos instalados em grade ou lista, com ícones e categorias.
- A pesquisa filtra nome, descrição, identificador e categoria.
- A ordenação oferece nome A–Z, nome Z–A e categoria.
- Cabeçalho dedicado à página e botão para exportar o inventário visual em CSV (separador `;`).
- Alternância funcional entre visualização em grade e lista.
- Ao selecionar um cartão, o painel lateral exibe descrição, identificador, origem, versão e estado.
- A página usa os arquivos `.desktop` para evitar tratar bibliotecas e dependências do APT como aplicativos gráficos.
- O inventário completo de pacotes APT/Flatpak continua disponível internamente e separado da lista visual.
- A interface permanece em modo de leitura: não instala, remove nem atualiza programas.
- A validação automatizada desta entrega passou em 5 testes; a validação visual GTK na VM Kali ainda precisa ser feita.
