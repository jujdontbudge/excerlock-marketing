import React, { useCallback, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Link from "@tiptap/extension-link";
import { marked } from "marked";
import TurndownService from "turndown";
import "./style.css";

const token = new URLSearchParams(location.search).get("token") || "";
const api = async (options = {}) => {
  const response = await fetch("/api/document", {
    ...options,
    headers: { authorization: `Bearer ${token}`, "content-type": "application/json", ...(options.headers || {}) }
  });
  const value = await response.json();
  if (!response.ok) throw Object.assign(new Error(value.error), { status: response.status, value });
  return value;
};
const turndown = new TurndownService({ headingStyle: "atx", bulletListMarker: "-", codeBlockStyle: "fenced", emDelimiter: "*" });
turndown.addRule("fencedCode", {
  filter: (node) => node.nodeName === "PRE" && node.firstElementChild?.nodeName === "CODE",
  replacement: (_content, node) => {
    const code = node.firstElementChild;
    const language = (code.className.match(/language-([\w-]+)/) || [])[1] || "";
    return `\n\n\`\`\`${language}\n${code.textContent.replace(/\n$/, "")}\n\`\`\`\n\n`;
  }
});

function App() {
  const [doc, setDoc] = useState(null);
  const [status, setStatus] = useState("Loading");
  const [draft, setDraft] = useState("");
  const timer = useRef();
  const revision = useRef("");
  const saving = useRef(false);
  const dirty = useRef(false);
  const editVersion = useRef(0);
  const draftRef = useRef("");
  const queued = useRef(false);
  const saveRef = useRef();
  const retryCount = useRef(0);
  const retryTimer = useRef();

  const save = useCallback(async () => {
    if (!dirty.current || !doc || doc.unsupported.length) return;
    if (saving.current) { queued.current = true; return; }
    saving.current = true;
    setStatus("Saving");
    const version = editVersion.current;
    const content = draftRef.current.replace(/\n{3,}/g, "\n\n").replace(/\s+$/, "") + "\n";
    let saved = false;
    try {
      const result = await api({ method: "PUT", body: JSON.stringify({ content, revision: revision.current }) });
      revision.current = result.revision;
      saved = true;
      if (editVersion.current === version) {
        dirty.current = false;
        retryCount.current = 0;
        setStatus("Saved");
      }
    } catch (error) {
      setStatus(error.status === 409 ? "Conflict" : "Error");
      if (error.status !== 409 && dirty.current && retryCount.current < 3) {
        const delay = 800 * (2 ** retryCount.current);
        retryCount.current += 1;
        clearTimeout(retryTimer.current);
        retryTimer.current = setTimeout(() => saveRef.current(), delay);
      }
    } finally {
      saving.current = false;
      const needsNextSave = saved && dirty.current && (queued.current || editVersion.current !== version);
      queued.current = false;
      if (needsNextSave) setTimeout(() => saveRef.current(), 0);
    }
  }, [doc]);
  saveRef.current = save;

  const editor = useEditor({
    extensions: [StarterKit, Link.configure({ openOnClick: false })],
    editable: !!doc && !doc.unsupported.length,
    content: "",
    onUpdate: ({ editor }) => {
      const markdown = turndown.turndown(editor.getHTML());
      setDraft(markdown);
      draftRef.current = markdown;
      editVersion.current += 1;
      retryCount.current = 0;
      clearTimeout(retryTimer.current);
      dirty.current = true;
      setStatus("Saving");
      clearTimeout(timer.current);
    }
  });

  useEffect(() => {
    api().then((value) => {
      setDoc(value);
      revision.current = value.revision;
      const md = value.content;
      setDraft(md);
      draftRef.current = md;
      editor?.commands.setContent(marked.parse(md), { emitUpdate: false });
      editor?.setEditable(!value.unsupported.length);
      setStatus(value.unsupported.length ? "Error" : "Saved");
    }).catch(() => setStatus("Error"));
  }, [editor]);
  useEffect(() => {
    if (!dirty.current) return;
    clearTimeout(timer.current);
    timer.current = setTimeout(save, 900);
    return () => clearTimeout(timer.current);
  }, [draft, save]);
  useEffect(() => () => clearTimeout(retryTimer.current), []);
  useEffect(() => {
    const key = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "s") { event.preventDefault(); save(); }
    };
    addEventListener("keydown", key);
    return () => removeEventListener("keydown", key);
  }, [save]);

  const button = (label, action, active) => <button className={active ? "active" : ""} onClick={action} type="button">{label}</button>;
  const copy = () => navigator.clipboard.writeText(draft);
  const reload = () => location.reload();
  if (!doc) return <main className="loading">{status}</main>;
  return <div className="app">
    <header><div><h1>{doc.title}</h1><p title={doc.absolutePath}>{doc.absolutePath}</p></div><span className={`status ${status.toLowerCase()}`}>{status}</span></header>
    <div className="notice"><b>One editor at a time:</b> a human and an agent must not edit this file simultaneously. To tile, use the green window button → Move &amp; Resize.</div>
    {doc.unsupported.length ? <div className="warning"><b>Editing disabled.</b> This file contains {doc.unsupported.join(", ")}. Rich editing could alter it, so no save will be attempted.</div> : null}
    {status === "Conflict" ? <div className="warning">The file changed on disk. <button onClick={reload}>Reload</button> <button onClick={copy}>Copy My Draft</button></div> : null}
    <nav>
      {button("H1", () => editor.chain().focus().toggleHeading({ level: 1 }).run(), editor.isActive("heading", { level: 1 }))}
      {button("H2", () => editor.chain().focus().toggleHeading({ level: 2 }).run(), editor.isActive("heading", { level: 2 }))}
      {button("B", () => editor.chain().focus().toggleBold().run(), editor.isActive("bold"))}
      {button("I", () => editor.chain().focus().toggleItalic().run(), editor.isActive("italic"))}
      {button("• List", () => editor.chain().focus().toggleBulletList().run(), editor.isActive("bulletList"))}
      {button("1. List", () => editor.chain().focus().toggleOrderedList().run(), editor.isActive("orderedList"))}
      {button("Quote", () => editor.chain().focus().toggleBlockquote().run(), editor.isActive("blockquote"))}
      {button("Code", () => editor.chain().focus().toggleCode().run(), editor.isActive("code"))}
      {button("Code block", () => editor.chain().focus().toggleCodeBlock().run(), editor.isActive("codeBlock"))}
      {button("Link", () => { const href = prompt("Link URL", editor.getAttributes("link").href || "https://"); if (href) editor.chain().focus().extendMarkRange("link").setLink({ href }).run(); }, editor.isActive("link"))}
      {button("Undo", () => editor.chain().focus().undo().run())}{button("Redo", () => editor.chain().focus().redo().run())}
    </nav>
    <article><EditorContent editor={editor}/></article>
  </div>;
}
createRoot(document.getElementById("root")).render(<App/>);
