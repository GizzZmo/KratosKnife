# KratosKnife

![KratosKnife Logo](https://img.shields.io/badge/Kratos-Knife-red.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

--- 

## 🗡️ Unleash the Power of Code Generation and Project Scaffolding

**KratosKnife** is a versatile and powerful command-line interface (CLI) tool designed to streamline and accelerate your development workflow. It specializes in rapid project scaffolding, code generation, and automating repetitive tasks, allowing you to focus on building features rather than setting up boilerplate.

Inspired by the legendary blades, KratosKnife provides sharp, precise, and efficient tools to cut through development friction, helping you generate robust project structures, components, modules, and more, with just a few commands.

## ✨ Features

*   **Rapid Project Scaffolding:** Quickly set up new projects with predefined templates (e.g., React, Vue, Node.js API, TypeScript library).
*   **Component & Module Generation:** Generate boilerplate for individual components, modules, services, or pages within existing projects.
*   **Customizable Templates:** Use built-in templates or define your own custom templates to match your team's conventions.
*   **Intelligent File Operations:** Smartly creates directories, writes files, and injects code snippets where necessary.
*   **Interactive Prompts:** Guided setup with interactive prompts for configuration options.
*   **Extensible Architecture:** Designed for easy extension and integration with other tools.
*   **Cross-Platform:** Works seamlessly on Windows, macOS, and Linux.

## 📖 Table of Contents

*   [Installation](#-installation)
*   [How to Use (Basic Usage)](#-how-to-use-basic-usage)
*   [Advanced Usage & Commands](#-advanced-usage--commands)
*   [Custom Templates](#-custom-templates)
*   [Contributing](#-contributing)
*   [License](#-license)

## 🚀 Installation

KratosKnife is a Node.js CLI tool. Ensure you have Node.js (v14 or higher) and npm (or yarn) installed on your system.

To install KratosKnife globally on your machine, open your terminal or command prompt and run:

```bash
npm install -g kratosknife
# OR
yarn global add kratosknife
```

After installation, you can verify it by running:

```bash
kratosknife --version
```

This should output the installed version of KratosKnife.

## 🔪 How to Use (Basic Usage)

KratosKnife provides several commands for different generation tasks. All commands follow a consistent pattern: `kratosknife <command> [name] [options]`.

### 1. Generating a New Project

To start a new project, use the `init` or `new` command. You'll be prompted to choose a project type and provide a project name.

```bash
kratosknife init my-new-app
```

Alternatively, you can specify the template directly:

```bash
kratosknife init my-react-app --template react
# Available templates: react, vue, node-api, ts-lib
```

This command will:
1.  Create a new directory named `my-new-app`.
2.  Download and scaffold the chosen template into that directory.
3.  Install necessary dependencies (if the template requires).
4.  Provide instructions on how to start your new project.

### 2. Generating Components/Modules within an Existing Project

Navigate into your project directory first. Then, use the `generate` or `g` command to create specific components, modules, or services.

For example, to generate a React component:

```bash
cd my-react-app
kratosknife generate component MyButton
```

This command will typically:
1.  Ask for the desired location (e.g., `src/components`, `src/views`).
2.  Generate `MyButton.js` (or `.tsx`), `MyButton.module.css` (or `.scss`), and `index.js` (or `index.ts`) files within a new `MyButton` directory.
3.  Inject necessary imports or exports if your template is configured to do so.

Other common generation commands:

*   **Generate a service (for Node.js API projects):**
    ```bash

    kratosknife g service UserService
    ```

*   **Generate a Vue component:**
    ```bash

    kratosknife g component NavBar --framework vue
    ```
    (Note: the `--framework` flag might be inferred from your project's `package.json` if configured, or can be explicitly provided).

*   **Generate a Redux slice:**
    ```bash

    kratosknife g slice auth
    ```

### 3. Listing Available Templates

To see all predefined templates and custom templates configured for your KratosKnife installation:

```bash
kratosknife list templates
```

## ⚙️ Advanced Usage & Commands

*   **Help Command:** Get detailed help for any command.
    ```bash
kratosknife --help
kratosknife generate --help
    ```

*   **Dry Run:** See what files would be generated without actually creating them.
    ```bash

    kratosknife g component MyNewComponent --dry-run
    ```

*   **Verbose Output:** Get more detailed logs during generation.
    ```bash

    kratosknife init my-app --verbose
    ```

## 📝 Custom Templates

KratosKnife allows you to define and use your own custom templates. This is incredibly powerful for maintaining consistent code standards across teams or personal projects.

To create a custom template, simply structure a directory with your desired files and use placeholders for dynamic content (e.g., `{{name}}`, `{{componentName}}`).

For example, create a template folder like `~/.kratosknife-templates/my-custom-react-component` with the following structure:

```
my-custom-react-component/
├── index.js
└── {{name}}.js
```

**`{{name}}.js` content:**

```javascript
import React from 'react';
import './{{name}}.css';

const {{componentName}} = () => {
  return (
    <div className="{{name}}-container">
      <h1>Hello from {{componentName}}!</h1>
    </div>
  );
};

export default {{componentName}};
```

Once created, you can register and use it:

```bash
kratosknife add template my-custom-component ~/.kratosknife-templates/my-custom-react-component
```

Then, generate using your custom template:

```bash
kratosknife g my-custom-component MyWidget
```

Refer to the [official documentation](link-to-docs) for a comprehensive guide on creating and managing custom templates, including available placeholders and configuration options.

## 🙌 Contributing

We welcome contributions to KratosKnife! Whether it's bug reports, feature requests, or pull requests, your help is invaluable.

To contribute:
1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Write tests for your changes (if applicable).
5.  Ensure all existing tests pass.
6.  Commit your changes (`git commit -m 'feat: Add new awesome feature'`).
7.  Push to the branch (`git push origin feature/your-feature-name`).
8.  Open a Pull Request.

Please ensure your code adheres to our coding standards and include appropriate documentation.

## 📜 License

KratosKnife is released under the [MIT License](https://opensource.org/licenses/MIT). See the `LICENSE` file for more details.

--- 

Made with ❤️ by GizzZmo and the KratosKnife Community.
