// Monaco code editor
const MonacoConfig = (function () {
  let monacoEditor;
  let debounceTimer;

  function initMonaco() {
    // Define the rules of Lox, so Monaco can perform syntax highlighting
    require.config({
      paths: { vs: "https://unpkg.com/monaco-editor@0.45.0/min/vs" },
    });

    require(["vs/editor/editor.main"], function () {
      try {
        monaco.languages.register({ id: "lox" });
        monaco.languages.setMonarchTokensProvider("lox", {
          tokenizer: {
            root: [
              [
                /\b(and|class|else|false|for|fun|if|nil|or|print|return|super|this|true|var|while)\b/,
                "keyword",
              ],

              [/[a-zA-Z_]\w*/, "identifier"],

              [/\d*\.\d+([eE][\-+]?\d+)?/, "number.float"],
              [/\d+/, "number"],

              [/"([^"\\]|\\.)*$/, "string.invalid"], // unterminated string
              [/"/, "string", "@string"],

              [/\/\/.*$/, "comment"],

              [/[{}()\[\]]/, "@brackets"],
              [/[<>]=?/, "operator"],
              [/[!=]=/, "operator"],
              [/[+\-*\/=]/, "operator"],
              [/[;,.]/, "delimiter"],

              [/[ \t\r\n]+/, "white"],
            ],

            string: [
              [/[^\\"]+/, "string"],
              [/\\./, "string.escape"],
              [/"/, "string", "@pop"],
            ],
          },
        });

        monaco.languages.setLanguageConfiguration("lox", {
          comments: {
            lineComment: "//",
          },
          brackets: [
            ["{", "}"],
            ["[", "]"],
            ["(", ")"],
          ],
          autoClosingPairs: [
            { open: "{", close: "}" },
            { open: "[", close: "]" },
            { open: "(", close: ")" },
            { open: '"', close: '"' },
          ],
          surroundingPairs: [
            { open: "{", close: "}" },
            { open: "[", close: "]" },
            { open: "(", close: ")" },
            { open: '"', close: '"' },
          ],
        });

        monacoEditor = monaco.editor.create(
          document.getElementById("lox-editor"),
          {
            value: "// Enter Lox code here, or try the examples below",
            language: "lox",
            theme: "vs",
            fontSize: 14,
            fontFamily: 'Monaco, Menlo, "Ubuntu Mono", Consolas, monospace',
            lineNumbers: "on",
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            insertSpaces: true,
            wordWrap: "on",
            wrappingIndent: "indent",
          }
        );

        monacoEditor.onDidChangeModelContent(() => {
          const code = monacoEditor.getValue();

          clearTimeout(debounceTimer);
          debounceTimer = setTimeout(() => {
            // Use a more robust way to call executeCode
            if (typeof window.executeCode === "function") {
              window.executeCode(code);
            } else {
              console.warn("executeCode function not available yet");
            }
          }, 50);
        });

        // Set initial message in output
        const outputEl = document.getElementById("output");
        if (outputEl) {
          outputEl.textContent = "Start typing Lox code to see results...";
        }
      } catch (error) {
        console.error("Failed to initialize Monaco editor:", error);
      }
    });
  }

  function setCode(code) {
    if (monacoEditor) {
      monacoEditor.setValue(code);
    } else {
      console.warn("Monaco editor not available yet");
    }
  }

  function loadExample(type) {
    if (window.ExamplesModule && window.ExamplesModule.hasExample(type)) {
      setCode(window.ExamplesModule.getExample(type));
    } else {
      console.warn(`Example '${type}' not found`);
    }
  }

  return {
    setCode,
    loadExample,
    initMonaco,
  };
})();

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", MonacoConfig.initMonaco);
} else {
  MonacoConfig.initMonaco();
}

window.setCode = MonacoConfig.setCode;
window.loadExample = MonacoConfig.loadExample;
