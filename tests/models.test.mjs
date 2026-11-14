import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Box3, Vector3 } from 'three';

for (const name of ['speech-frame','headset','messenger','printer']) {
  test(`3D model ${name} parses with renderable geometry and finite bounds`,async()=>{
    const bytes = await readFile(new URL(`../dist/media/3d/${name}.glb`,import.meta.url));
    const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
    const model = await new GLTFLoader().parseAsync(buffer,'');
    let meshes=0, vertices=0;
    model.scene.traverse(object=>{ if(object.isMesh) { meshes++; vertices+=object.geometry.attributes.position.count; assert(object.material); } });
    assert(meshes>0 && vertices>100);
    const size = new Box3().setFromObject(model.scene).getSize(new Vector3());
    assert([size.x,size.y,size.z].every(value=>Number.isFinite(value)&&value>0));
  });
}
