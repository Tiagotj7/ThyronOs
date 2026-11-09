<div align="center">

# THYRON OS

**LIBERDADE • DESEMPENHO • INOVAÇÃO**

*Uma experiência Linux personalizada sobre Kali Linux e GNOME.*

![Status](https://img.shields.io/badge/status-early%20planning-075BFF)
![Base](https://img.shields.io/badge/base-Kali%20Linux-0B1425)
![Desktop](https://img.shields.io/badge/desktop-GNOME-00C8FF)
![License](https://img.shields.io/badge/license-GPL--3.0--or--later-lightgrey)

</div>

> **Aviso de estágio:** este repositório contém a estrutura inicial e o planejamento do projeto. Não representa uma ISO pronta, nem componentes funcionais já implementados.

## Visão geral

THYRON OS é o projeto de uma distribuição Linux personalizada baseada em **Kali Linux**, com **GNOME** como ambiente gráfico principal. Seu objetivo é combinar uma experiência desktop própria, identidade visual Electric Blue, personalização modular e acesso responsável às ferramentas disponíveis na base Kali.

O projeto pretende ir além de uma simples troca de papel de parede: a experiência THYRON deverá incluir componentes próprios, perfis visuais, configurações integradas e uma seleção consciente de aplicativos.

## Decisões do projeto

| Decisão | Definição |
|---|---|
| Repositório | Público |
| Estratégia | Estrutura completa desde o início; implementação incremental |
| Sistema-base | Kali Linux |
| Ambiente gráfico | GNOME |
| Aparência inicial | THYRON Modern, modo escuro |
| Identidade | Electric Blue |
| Primeira entrega | ISO Live experimental, sem instalação no disco como requisito |
| Instalador | Avaliar posteriormente; não faz parte do primeiro marco |

## Identidade visual

| Nome | Cor |
|---|---|
| Deep Black | `#050914` |
| Night Blue | `#0B1425` |
| Electric Blue | `#075BFF` |
| Neon Cyan | `#00C8FF` |
| Metallic Silver | `#DCE5F2` |

Mascote planejado: lobo preto e prateado com olhos azuis. Estilo padrão: **THYRON Modern**.

## O que está planejado

- THYRON Desktop sobre GNOME.
- Dock inferior centralizado e painel superior coerentes com a identidade.
- Seis perfis: Classic, Modern, Futuristic, Minimal, Pro e Gaming.
- THYRON Style Center para gerenciar aparência e restaurar preferências.
- THYRON Store com integração real a APT e Flatpak.
- Terminal GNOME Terminal com ZSH e paleta THYRON.
- Personalização cuidadosa de GDM e bloqueio, preservando autenticação e recuperação.
- ISO Live personalizada para avaliação em máquina virtual.

Consulte [`documentation/ROADMAP.md`](documentation/ROADMAP.md) para etapas e critérios de conclusão.

## Estado atual

**Fase: preparação do repositório.** A estrutura, os documentos e os pontos de extensão estão sendo organizados. Dependências, componentes, ISO e testes ainda precisam ser implementados e verificados.

Não considere itens planejados como concluídos. O progresso deve ser atualizado com evidências em Issues e Pull Requests.

## Arquitetura

```text
branding/       Identidade visual e ativos
core/           Configurações, perfis, serviços e recuperação
desktop/        Integração GNOME, extensões e GDM
applications/   Aplicativos THYRON
themes/         Seis perfis visuais
terminal/       Configuração do terminal e ZSH
packages/       Pacotes Debian próprios
iso/            Configuração do Kali Live Build
installer/      Pesquisa e integração futura do instalador
scripts/        Automação local de desenvolvimento e validação
tests/          Testes automatizados e roteiros manuais
documentation/  Arquitetura, decisões, testes e releases
```

Detalhes: [`documentation/ARCHITECTURE.md`](documentation/ARCHITECTURE.md).

## Primeira ISO: objetivo

A primeira imagem será **Live e experimental**, construída com ferramentas oficiais compatíveis com Kali. O foco inicial é comprovar:

1. A ISO inicia em uma máquina virtual.
2. A sessão GNOME abre sem falhas críticas.
3. O tema e os ativos THYRON são aplicados de forma consistente.
4. A rede e os recursos básicos continuam funcionais.
5. O sistema pode ser encerrado sem alterações no computador hospedeiro.

A ISO não será considerada pronta para instalação diária. O instalador será avaliado em uma etapa posterior.

Leia [`documentation/ISO_FIRST_BUILD.md`](documentation/ISO_FIRST_BUILD.md).

## Ambiente de desenvolvimento

Antes de instalar ferramentas ou alterar configurações, identifique o sistema hospedeiro. Execute o diagnóstico somente para leitura:

```bash
echo "===== SISTEMA OPERACIONAL ====="
cat /etc/os-release
echo
echo "===== ARQUITETURA ====="
uname -m
echo
echo "===== PROCESSADOR ====="
lscpu | grep -E 'Model name|CPU\\(s\\)'
echo
echo "===== MEMÓRIA ====="
free -h
echo
echo "===== ARMAZENAMENTO ====="
df -hT
echo
echo "===== DISCOS E PARTIÇÕES ====="
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
echo
echo "===== GERENCIADORES DE PACOTES ====="
command -v apt; command -v dnf; command -v pacman; command -v zypper
echo
echo "===== FERRAMENTAS ====="
git --version
python3 --version
```

Não é necessário instalar Kali no computador de desenvolvimento. Preserve o sistema atual e faça os primeiros testes em VM. O hardware informado no planejamento (8 GB RAM e 128 GB de armazenamento) é preliminar; a distribuição hospedeira e o espaço livre ainda precisam ser confirmados.

## Como contribuir

1. Leia [`CONTRIBUTING.md`](CONTRIBUTING.md).
2. Consulte as decisões em [`documentation/DECISIONS.md`](documentation/DECISIONS.md).
3. Abra uma Issue antes de mudanças estruturais.
4. Trabalhe em branch própria e envie Pull Request.
5. Inclua evidências de testes e atualize a documentação.

## Segurança e uso responsável

As ferramentas herdadas do Kali devem ser usadas apenas em ambientes próprios, de laboratório ou com autorização explícita. Consulte [`SECURITY.md`](SECURITY.md) para reportar problemas.

## Licença e marcas

O código original deste projeto é proposto sob GPL-3.0-or-later, salvo indicação diferente em diretórios específicos. Ativos visuais poderão receber licença própria quando forem adicionados. Componentes de terceiros mantêm suas respectivas licenças.

THYRON OS é um projeto independente. Kali Linux, Debian, GNOME e demais marcas citadas pertencem aos respectivos titulares. Este projeto não declara afiliação ou endosso por essas organizações.

---

**Próximo marco:** validar o ambiente de desenvolvimento, inicializar o Git e preparar a configuração inicial do Kali Live Build em uma branch dedicada.
