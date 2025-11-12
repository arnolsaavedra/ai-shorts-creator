# 🤝 Contributing to AI Shorts Creator

First off, thank you for considering contributing to AI Shorts Creator! It's people like you that make this tool better for everyone.

[🇪🇸 Versión en Español](#-contribuir-a-ai-shorts-creator-español) | [Skip to Spanish version](#-contribuir-a-ai-shorts-creator-español)

---

## 🌟 Ways to Contribute

### 🐛 Reporting Bugs

If you find a bug, please create an issue with:

- **Clear title**: Describe the bug in one sentence
- **Description**: Detailed explanation of what happened
- **Steps to reproduce**: List the exact steps to trigger the bug
- **Expected behavior**: What should have happened
- **Actual behavior**: What actually happened
- **Screenshots**: If applicable
- **Environment**:
  - OS: (e.g., Windows 10, macOS 13, Ubuntu 22.04)
  - Python version: (e.g., 3.9.13)
  - Browser: (e.g., Chrome 120)

### 💡 Suggesting Features

Have an idea? Create an issue with:

- **Feature description**: What you want to add
- **Use case**: Why it would be useful
- **Alternatives**: Other solutions you've considered
- **Additional context**: Any relevant information

### 🔧 Pull Requests

1. **Fork the repository**
   ```bash
   # Fork via GitHub UI, then clone your fork
   ```

2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/ai-shorts-creator.git
   cd ai-shorts-creator
   ```

3. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

4. **Make your changes**:
   - Follow the existing code style
   - Add comments where necessary
   - Update documentation if needed

5. **Test your changes**:
   ```bash
   # Make sure the app runs
   python app.py

   # Test the feature manually
   # Try edge cases
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: description of your changes"
   ```

   **Commit message format**:
   - `Add: new feature description`
   - `Fix: bug description`
   - `Update: improvement description`
   - `Docs: documentation changes`
   - `Refactor: code refactoring`
   - `Test: adding or updating tests`

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request**:
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template with:
     - What changes you made
     - Why you made them
     - How to test them
     - Screenshots (if UI changes)

---

## 📝 Code Style Guidelines

### Python

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to all functions
- Keep functions small and focused (single responsibility)
- Use type hints where appropriate

**Example**:
```python
def generate_viral_title(segment_text: str, language: str = 'auto') -> str:
    """
    Generate a viral title using AI based on segment content.

    Args:
        segment_text (str): Text content of the video segment
        language (str): Target language ('auto', 'es', 'en'). Defaults to 'auto'.

    Returns:
        str: Generated viral title

    Raises:
        ValueError: If segment_text is empty
        APIError: If OpenAI API call fails
    """
    if not segment_text:
        raise ValueError("Segment text cannot be empty")

    # Implementation
    pass
```

### JavaScript

- Use ES6+ features (const, let, arrow functions, etc.)
- Use `const` for constants, `let` for variables, avoid `var`
- Use meaningful variable names (e.g., `videoFile` not `vf`)
- Add comments for complex logic
- Use async/await instead of promise chains

**Example**:
```javascript
async function uploadVideo(file) {
    const formData = new FormData();
    formData.append('video', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        return await response.json();
    } catch (error) {
        console.error('Upload failed:', error);
        throw error;
    }
}
```

### HTML/CSS

- Use semantic HTML5 tags (`<header>`, `<main>`, `<section>`, etc.)
- Keep CSS organized and commented
- Use meaningful class names (BEM or similar methodology)
- Maintain responsive design principles
- Test on multiple screen sizes

---

## 🧪 Testing

While we don't have automated tests yet (**contributions welcome!**), please:

1. **Test your changes manually**:
   - Run the app and verify the feature works
   - Test with different inputs
   - Try to break it!

2. **Test edge cases**:
   - Empty inputs
   - Very large files
   - Different video formats
   - Network failures
   - Invalid API keys

3. **Test on different environments** (if possible):
   - [ ] Windows
   - [ ] Linux
   - [ ] macOS
   - [ ] Different browsers (Chrome, Firefox, Safari, Edge)

4. **Document what you tested** in your PR description

---

## 📚 Documentation

If you add a new feature or change existing functionality:

1. **Update README.md** with:
   - New feature description
   - Usage instructions
   - Configuration options
   - Examples

2. **Add comments in the code**:
   - Explain complex logic
   - Document function parameters and return values
   - Add inline comments for non-obvious code

3. **Update .env.example** if:
   - You add new environment variables
   - You change existing variable names

4. **Consider adding examples**:
   - Usage examples
   - Code snippets
   - Screenshots/GIFs

---

## 🎯 Priority Areas for Contribution

We especially welcome contributions in these areas:

### High Priority
- [ ] **Tests**: Unit tests, integration tests, end-to-end tests
- [ ] **Documentation**: Tutorials, video guides, translations
- [ ] **Bug fixes**: Check [open issues](https://github.com/your-username/ai-shorts-creator/issues)

### Medium Priority
- [ ] **Performance**: Optimization, caching, parallel processing
- [ ] **Features**: See [Roadmap](README.md#-roadmap--future-improvements)
- [ ] **UI/UX**: Design improvements, accessibility

### Nice to Have
- [ ] **Internationalization**: More language translations
- [ ] **CI/CD**: GitHub Actions workflows
- [ ] **Docker**: Containerization improvements
- [ ] **API**: REST API documentation

---

## 💬 Communication

### Where to Ask Questions?

- **General questions**: Open a [Discussion](https://github.com/your-username/ai-shorts-creator/discussions)
- **Bug reports**: Open an [Issue](https://github.com/your-username/ai-shorts-creator/issues)
- **Feature requests**: Open an [Issue](https://github.com/your-username/ai-shorts-creator/issues) with `enhancement` label
- **Security issues**: Email directly (see README for contact)

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards other contributors

---

## 🏆 Recognition

Contributors will be:
- Listed in the README.md
- Mentioned in release notes
- Credited in commit history
- Given proper attribution for their work

---

## 📋 Pull Request Checklist

Before submitting a PR, make sure:

- [ ] Code follows the style guidelines
- [ ] Comments are added for complex logic
- [ ] Documentation is updated (if needed)
- [ ] Manual testing is done
- [ ] No sensitive data (API keys, passwords) is committed
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains what and why

---

## 🚀 Getting Started with Development

### First Time Setup

```bash
# 1. Fork and clone
git clone https://github.com/your-username/ai-shorts-creator.git
cd ai-shorts-creator

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Add your API keys to .env

# 5. Run the app
python app.py
```

### Development Workflow

```bash
# 1. Create a branch for your work
git checkout -b feature/my-awesome-feature

# 2. Make changes and commit often
git add .
git commit -m "Add: specific change description"

# 3. Keep your fork updated
git fetch upstream
git rebase upstream/main

# 4. Push to your fork
git push origin feature/my-awesome-feature

# 5. Open a PR on GitHub
```

---

## ❓ Questions?

If you have questions about contributing:

- Check existing [Issues](https://github.com/your-username/ai-shorts-creator/issues)
- Open a [Discussion](https://github.com/your-username/ai-shorts-creator/discussions)
- Read the [README.md](README.md)
- Contact the maintainers

---

## 🙏 Thank You!

Every contribution, no matter how small, is valuable and appreciated!

Your time and effort help make this project better for everyone. 🎉

---

---

# 🤝 Contribuir a AI Shorts Creator (Español)

¡Gracias por considerar contribuir a AI Shorts Creator! Son personas como tú las que hacen esta herramienta mejor para todos.

---

## 🌟 Formas de Contribuir

### 🐛 Reportar Bugs

Si encuentras un bug, crea un issue con:

- **Título claro**: Describe el bug en una oración
- **Descripción**: Explicación detallada de qué pasó
- **Pasos para reproducir**: Lista los pasos exactos para activar el bug
- **Comportamiento esperado**: Qué debería haber pasado
- **Comportamiento actual**: Qué realmente pasó
- **Screenshots**: Si aplica
- **Entorno**:
  - OS: (ej., Windows 10, macOS 13, Ubuntu 22.04)
  - Versión de Python: (ej., 3.9.13)
  - Navegador: (ej., Chrome 120)

### 💡 Sugerir Funcionalidades

¿Tienes una idea? Crea un issue con:

- **Descripción de la funcionalidad**: Qué quieres agregar
- **Caso de uso**: Por qué sería útil
- **Alternativas**: Otras soluciones que consideraste
- **Contexto adicional**: Cualquier información relevante

### 🔧 Pull Requests

1. **Haz fork del repositorio**
2. **Clona tu fork**:
   ```bash
   git clone https://github.com/tu-usuario/ai-shorts-creator.git
   cd ai-shorts-creator
   ```

3. **Crea una rama**:
   ```bash
   git checkout -b feature/nombre-de-tu-feature
   # o
   git checkout -b fix/tu-bug-fix
   ```

4. **Haz tus cambios**:
   - Sigue el estilo de código existente
   - Agrega comentarios donde sea necesario
   - Actualiza la documentación si es necesario

5. **Prueba tus cambios**:
   ```bash
   # Asegúrate que la app funciona
   python app.py

   # Prueba la funcionalidad manualmente
   ```

6. **Commit tus cambios**:
   ```bash
   git add .
   git commit -m "Add: descripción de tus cambios"
   ```

   **Formato de mensajes de commit**:
   - `Add: nueva funcionalidad`
   - `Fix: descripción del bug`
   - `Update: descripción de la mejora`
   - `Docs: cambios en documentación`

7. **Push a tu fork**:
   ```bash
   git push origin feature/nombre-de-tu-feature
   ```

8. **Abre un Pull Request**:
   - Ve al repositorio original
   - Haz clic en "New Pull Request"
   - Selecciona tu rama
   - Llena el template del PR

---

## 📝 Guías de Estilo de Código

### Python
- Sigue [PEP 8](https://pep8.org/)
- Usa nombres de variables significativos
- Agrega docstrings a las funciones
- Mantén las funciones pequeñas y enfocadas

### JavaScript
- Usa características ES6+
- Usa `const` y `let`, evita `var`
- Usa nombres de variables significativos
- Agrega comentarios para lógica compleja

### HTML/CSS
- Usa etiquetas semánticas HTML5
- Mantén el CSS organizado y comentado
- Mantén el diseño responsivo

---

## 🧪 Testing

Aunque no tenemos tests automatizados todavía (¡contribuciones bienvenidas!), por favor:

1. Prueba tus cambios manualmente
2. Prueba casos extremos
3. Prueba en diferentes navegadores (si es frontend)
4. Prueba con diferentes formatos/tamaños de video

---

## 📚 Documentación

Si agregas una nueva funcionalidad:

1. Actualiza README.md con instrucciones de uso
2. Agrega comentarios en el código
3. Actualiza .env.example si se necesitan nuevas variables
4. Considera agregar ejemplos

---

## 🎯 Áreas Prioritarias para Contribuir

Especialmente bienvenidas contribuciones en:

- [ ] **Tests**: Tests unitarios, de integración
- [ ] **Documentación**: Tutoriales, ejemplos, traducciones
- [ ] **Performance**: Optimización, caching
- [ ] **Funcionalidades**: Ver [Roadmap](README_ES.md#-roadmap-y-mejoras-futuras)
- [ ] **Bug fixes**: Revisa los issues abiertos
- [ ] **UI/UX**: Mejoras de diseño

---

## ❓ ¿Preguntas?

Si tienes preguntas sobre contribuir:

- Abre una discusión en GitHub Discussions
- Revisa los issues existentes para preguntas similares
- Contacta a los mantenedores

---

## 🙏 ¡Gracias!

Cada contribución, sin importar qué tan pequeña, es valiosa y apreciada!
