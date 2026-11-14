# Asset and dependency notes

- Chatversio branding: original logo supplied by the user; the transparent footer logo was sourced from the company's original website. Keep the supplied artwork.
- Agency portraits and product media: the approved website's generated illustrations and Blender-rendered assets are included. The human illustrations are raster artwork, not fully rigged human 3D models.
- Three.js 0.180.0: MIT; see `licenses/Three-MIT.txt`. Its license banner is also retained in the bundled scene.
- esbuild 0.25.9: MIT; see `licenses/Esbuild-MIT.txt`. This is a build tool, not a browser dependency.
- Font licenses: included under `dist/fonts/` for Inter, Plus Jakarta Sans and the editorial font.
- Footer icons: Font Awesome Free 7.0.1 SVG shapes; see `dist/media/footer-icons-license.txt`.
- Generated dialogue source: the optional `art/voice_samples.py` identifies sherpa-onnx and the Kokoro model used for generation. The finished audio is bundled. Model weights and regeneration tooling are not bundled; acquire and review those dependencies separately if regenerating audio.

No live-service credentials, source repository tokens, Git history or customer data are included. Original website content and company links belong to Chatversio's existing marketing materials.
