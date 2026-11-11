# THYRON Store

Primeiro esqueleto técnico da central de aplicativos do THYRON OS.

## Estado desta entrega

- Interface GTK 4 inicial: em desenvolvimento.
- Descoberta de aplicativos `.desktop`: implementada no módulo de catálogo.
- Inventário APT/dpkg: consulta somente leitura.
- Inventário Flatpak: consulta somente leitura, se o comando estiver disponível.
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

## Próximas etapas

1. Validar a execução GTK 4 na VM Kali.
2. Melhorar metadados e deduplicação de aplicativos.
3. Projetar a camada de operações com autorização via PolicyKit.
4. Só então implementar operações APT/Flatpak e testes em VM descartável.
