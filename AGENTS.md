# AGENTS.md

## Communication
- Respond to the user **in Spanish** at all times, regardless of the language of the code, files, or prompts.

## Repository state
- This workspace contains **only insurance source data** — no application code, package manifests, build, tests, linters, CI, or `opencode.json`. Do not invent commands; confirm the intended stack before scaffolding.
- Git is **not initialized** here. On this Windows machine `git` is not on PATH; invoke it as `& "C:\Program Files\Git\cmd\git.exe"`.

## Source data (treat as read-only inputs)
- `Insumos_Control_Polizas/Maestro_Clientes.xlsx` — sheet1, header + 20 clients. Columns A–E: `Cedula | Nombre_Completo | Correo | Telefono | Asesor`. IDs `N-NNNN-NNNN`, phones `NNNN-NNNN`. Strings are ASCII-folded (no accents: "Umana", "Bolanos"); asesores are Karla Umana, Diego Chaves, Mariana Solis.
- `Insumos_Control_Polizas/polizas/*.pdf` — 20 single-page, text-based ReportLab PDFs (not scans). Filename is `Poliza_<policy-id>.pdf`.

## Policy schema and ID convention
- Policy ID: `<ISSUER>-<YYYY>-<NNNN>`. Prefix → issuer: `AIS` = Aseguradora del Istmo S.A. (5), `PCS` = Proteccion Caribe S.A. (9), `SPC` = Seguros Pacifico Central S.A. (6).
- Fixed Spanish labels in this order: `Numero de poliza`, `Ramo`, `Tomador / Asegurado`, `Cedula`, `Vigencia desde`, `Vigencia hasta`, `Prima anual`, `Forma de pago`, `Suma asegurada`, `Intermediario`, `Asesor`, `Coberturas principales`.
- Formats: dates `DD/MM/YYYY`; money `CRC 1,234,567.00`. Every policy's intermediary is `Corredora de Seguros Horizonte`. Ramos: Automovil, Salud, Vida, Responsabilidad Civil, Hogar. Payment: Anual, Semestral, Mensual.

## Known data anomalies (verified; treat as validation cases, do not silently "fix")
- `PCS-2026-0009` is issued to `Roberto Fantasma Perez`, cedula `9-0000-0001`, who is **not** in the client master (ghost record).
- `AIS-2026-0002` has an **empty** `Prima anual` value; when parsing, the next token is the `Forma de pago` label, so adjacent-label parsing will misassign it.
- Master client `1-0321-0654 Javier Espinoza Leon` has no policy. The other 19 master clients have exactly one policy each.

## Reading the PDFs
- Python and `pdftotext` are unavailable on this machine. Content streams use `/Filter [/ASCII85Decode /FlateDecode]`; decode with PowerShell/.NET (ASCII85 manually, then `DeflateStream` after skipping the 2-byte zlib header) and read `(...) Tj` operators.
