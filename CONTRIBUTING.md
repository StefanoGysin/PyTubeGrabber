# Guia de Contribuição

Obrigado pelo interesse em contribuir para o PyTubeGrabber! Este documento fornece diretrizes para contribuir com o projeto.

## Código de Conduta

Ao participar deste projeto, você concorda em manter um ambiente respeitoso e colaborativo.

## Como Contribuir

### Relatando Bugs

1. **Verifique se o bug já foi relatado** na seção de Issues
2. **Crie uma nova issue** caso não exista
   - Use um título claro e descritivo
   - Descreva os passos para reproduzir o problema
   - Forneça informações do ambiente (sistema operacional, Python, FFmpeg)
   - Se possível, inclua capturas de tela

### Sugerindo Melhorias

1. **Crie uma issue** descrevendo sua ideia
2. **Explique o comportamento atual** e o que você gostaria de ver implementado
3. **Justifique** por que essa melhoria seria útil para a maioria dos usuários

### Submetendo Alterações

1. **Fork** o repositório
2. **Clone** seu fork localmente
3. **Crie uma branch** para sua contribuição:
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```
4. **Implemente** suas alterações, seguindo o estilo do código
5. **Adicione testes** quando aplicável
6. **Documente** o código usando docstrings
7. **Atualize a documentação** quando necessário
8. **Commit** suas alterações com mensagens claras:
   ```bash
   git commit -m "feat: adiciona funcionalidade de download de legendas"
   ```
9. **Push** para sua branch:
   ```bash
   git push origin feature/nova-funcionalidade
   ```
10. **Abra um Pull Request** para a branch principal do projeto

## Padrões de Codificação

- Siga as convenções PEP 8 para código Python
- Use type hints quando possível
- Documente funções e classes usando docstrings no formato NumPy/Google
- Use nomes significativos para variáveis, funções e classes
- Escreva testes unitários para novas funcionalidades
- Mantenha o código compatível com Python 3.6+

## Estrutura dos Commits

Use mensagens de commit claras e descritivas, seguindo o formato:

```
<tipo>: <descrição>

[corpo opcional]

[rodapé opcional]
```

Onde `<tipo>` pode ser:
- **feat**: Nova funcionalidade
- **fix**: Correção de bug
- **docs**: Alterações na documentação
- **style**: Formatação, ponto e vírgula, etc. (sem alteração no código)
- **refactor**: Refatoração de código
- **test**: Adição ou correção de testes
- **chore**: Alterações no processo de build, ferramentas, etc.

## Revisão de Pull Requests

Os mantenedores revisarão seu PR o mais rápido possível. Durante a revisão:
- Verifique se os testes estão passando
- Responda a quaisquer perguntas ou solicitações de alterações
- Seu PR pode precisar ser atualizado se houver conflitos com a branch principal

## Obrigado!

Suas contribuições são essenciais para tornar o PyTubeGrabber melhor para todos! 