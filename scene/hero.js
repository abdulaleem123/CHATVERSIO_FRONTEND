import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const stage = document.querySelector('.cast-stage');
const canvas = stage?.querySelector('.hero-3d');
const isEconomy = navigator.connection?.saveData === true;

if (canvas && !isEconomy) {
  mountStage().catch(() => {
    delete stage.dataset.webgl;
    canvas.hidden = true;
    document.dispatchEvent(new Event('ambientchange'));
  });
}

async function mountStage() {
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      canvas, alpha: true, antialias: true, powerPreference: 'low-power',
    });
  } catch {
    return;
  }
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.18;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, .1, 60);
  camera.position.set(0, .15, 10.8);
  camera.lookAt(0, .12, 0);
  const world = new THREE.Group();
  scene.add(world);

  const environmentScene = new RoomEnvironment();
  const pmrem = new THREE.PMREMGenerator(renderer);
  const environment = pmrem.fromScene(environmentScene, .05);
  scene.environment = environment.texture;
  scene.environmentIntensity = .82;
  environmentScene.dispose();
  pmrem.dispose();

  scene.add(new THREE.HemisphereLight(0xe7f5ff, 0x071933, 1.55));
  const key = new THREE.DirectionalLight(0xf1f8ff, 4.2);
  key.position.set(-3, 5, 4);
  scene.add(key);
  const rim = new THREE.DirectionalLight(0x46caff, 3.0);
  rim.position.set(4, 2, -2);
  scene.add(rim);
  const bounce = new THREE.PointLight(0x308bff, 28, 14, 2);
  bounce.position.set(-2, -1.5, 2.6);
  scene.add(bounce);

  const gltf = new GLTFLoader();
  const textureLoader = new THREE.TextureLoader();
  const roles = ['chat', 'sales', 'voice'];
  const modelNames = ['speech-frame', 'messenger', 'printer', 'headset'];
  const pendingModels = modelNames.map(name => gltf.loadAsync('/media/3d/' + name + '.glb'));
  const pendingTextures = roles.map(role => textureLoader.loadAsync('/media/agent-' + role + '.webp'));

  let loaded;
  try {
    loaded = await Promise.all([...pendingModels, ...pendingTextures]);
  } catch (error) {
    renderer.dispose();
    environment.dispose();
    throw error;
  }

  function modelAt(index) {
    const root = loaded[index].scene;
    root.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(root);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    root.position.sub(center);
    const wrapper = new THREE.Group();
    wrapper.add(root);
    wrapper.userData.span = Math.max(size.x, size.y, size.z);
    root.traverse(object => {
      if (!object.isMesh) return;
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      for (const material of materials) {
        material.envMapIntensity = 1.35;
        if (material.name === 'Mirror edge') material.roughness = .19;
        if (material.name.includes('phosphor')) material.emissiveIntensity = .8;
      }
    });
    world.add(wrapper);
    return wrapper;
  }

  const frame = modelAt(0);
  const frameMaterials = [];
  frame.traverse(object => {
    if (!object.isMesh) return;
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    for (const material of materials) {
      material.metalness = .86;
      material.roughness = .22;
      material.envMapIntensity = 1.6;
      if (material.name === 'Pearl titanium') frameMaterials.push(material);
    }
  });

  const props = {
    chat: modelAt(1),
    sales: modelAt(2),
    voice: modelAt(3),
  };

  // The rising pixels echo the mosaic at the top of the CV logo.
  const pixelGeometry = new THREE.BoxGeometry(.15, .15, .15);
  const pixelMaterial = new THREE.MeshStandardMaterial({
    color: 0x47c3ff, metalness: .65, roughness: .24,
    emissive: 0x08365e, emissiveIntensity: .35,
  });
  const pixels = [[1.42, 2.02], [1.69, 2.02], [1.69, 2.30],
    [1.96, 2.30], [1.96, 2.58], [2.22, 2.58]].map(([x, y], i) => {
    const pixel = new THREE.Mesh(pixelGeometry, pixelMaterial);
    pixel.userData = {x, y, phase: i * .7};
    pixel.position.set(x, y, -.4);
    world.add(pixel);
    return pixel;
  });

  const portraits = roles.map((role, i) => {
    const texture = loaded[modelNames.length + i];
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = Math.min(4, renderer.capabilities.getMaxAnisotropy());
    const material = new THREE.MeshBasicMaterial({
      map: texture, transparent: true, depthWrite: false, toneMapped: false,
      opacity: i === 0 ? 1 : 0,
    });
    material.onBeforeCompile = shader => {
      shader.fragmentShader = shader.fragmentShader.replace(
        '#include <alphamap_fragment>',
        '#include <alphamap_fragment>\n diffuseColor.a *= smoothstep(0.0, 0.15, vMapUv.y);',
      );
    };
    const plane = new THREE.Mesh(new THREE.PlaneGeometry(4.4, 4.4), material);
    plane.position.set(.10, .17, .12);
    plane.renderOrder = 2;
    world.add(plane);
    return plane;
  });

  const glow = new THREE.PointLight(0x52d6ff, 7, 7, 2);
  glow.position.set(1.5, 2.5, 1);
  scene.add(glow);

  const pose = {
    chat: {color: 0x75b1ff, highlight: 0x37b8ff},
    sales: {color: 0x3884ec, highlight: 0x6adfff},
    voice: {color: 0x88dfff, highlight: 0x89dbff},
    gear: {color: 0x7bb4f5, highlight: 0x52c9ff},
  };
  const currentColor = new THREE.Color(pose.chat.color);
  const targetColor = currentColor.clone();
  const highlightColor = new THREE.Color(pose.chat.highlight);
  let selected = stage.dataset.current || 'chat';
  let rotationTarget = -.53;
  let rotationCurrent = rotationTarget;
  let pointerX = 0;
  let pointerY = 0;
  let scrollDepth = 0;
  let phase = 0;
  let entrance = 0;
  let visible = true;
  let frameRequest = 0;
  let lastTime = 0;
  let disposed = false;
  let settleFrames = 0;
  const smallScreen = matchMedia('(max-width: 720px)');
  const finePointer = matchMedia('(pointer: fine)');

  function isMoving() {
    return document.body.dataset.motion === 'on';
  }

  function sizeCanvas() {
    const box = canvas.getBoundingClientRect();
    const width = Math.max(1, Math.round(box.width));
    const height = Math.max(1, Math.round(box.height));
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, smallScreen.matches ? 1.3 : 1.6));
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    // Maintain portrait size in both the landscape stage and narrow phone layout.
    camera.position.z = camera.aspect < 1.1 ? 11.8 : 10.8;
    camera.updateProjectionMatrix();
    wake();
  }

  function setView() {
    selected = stage.dataset.current || 'chat';
    targetColor.set(pose[selected].color);
    highlightColor.set(pose[selected].highlight);
    settleFrames = 55;
    wake();
  }

  function setProp(prop, position, size, rotation, blend) {
    prop.position.lerp(new THREE.Vector3(...position), blend);
    const scalar = size / prop.userData.span;
    prop.scale.lerp(new THREE.Vector3(scalar, scalar, scalar), blend);
    prop.rotation.x = THREE.MathUtils.lerp(prop.rotation.x, rotation[0], blend);
    prop.rotation.y = THREE.MathUtils.lerp(prop.rotation.y, rotation[1], blend);
    prop.rotation.z = THREE.MathUtils.lerp(prop.rotation.z, rotation[2], blend);
    prop.visible = prop.scale.x > .004;
  }

  function render(time) {
    frameRequest = 0;
    if (disposed || !visible || document.hidden || document.body.classList.contains('film-open')) {
      lastTime = 0;
      return;
    }
    const moving = isMoving();
    const interval = smallScreen.matches ? 1000 / 30 : 1000 / 45;
    if (moving && lastTime && time - lastTime < interval) {
      frameRequest = requestAnimationFrame(render);
      return;
    }
    const delta = Math.min(lastTime ? (time - lastTime) / 1000 : .033, .065);
    lastTime = time;
    if (moving) phase += delta;
    entrance = moving ? Math.min(1, entrance + delta * .77) : 1;
    const intro = 1 - Math.pow(1 - entrance, 3);
    const blend = moving ? 1 - Math.exp(-delta * 7) : 1;
    const drift = moving ? Math.sin(phase * .57) * .025 : 0;
    const isGear = selected === 'gear';

    currentColor.lerp(targetColor, blend);
    frameMaterials.forEach(material => material.color.copy(currentColor));
    rim.color.lerp(highlightColor, blend);
    glow.color.lerp(highlightColor, blend);
    frame.position.set(.04, .17 + drift, -.65);
    frame.rotation.set(.03, -.27 + pointerX * .10 + (1 - intro) * .65, -.14);
    frame.scale.setScalar(1.13 + .025 * Math.sin(phase * .32));
    world.rotation.y = THREE.MathUtils.lerp(world.rotation.y, moving ? pointerX * .065 : 0, blend);
    world.rotation.x = THREE.MathUtils.lerp(world.rotation.x, moving ? -pointerY * .025 : 0, blend);
    world.position.y = THREE.MathUtils.lerp(world.position.y, moving ? scrollDepth * .14 : 0, blend);
    key.position.x = -3 + pointerX * 2.5;
    bounce.position.x = -2 + pointerX * 1.7;
    rotationCurrent = THREE.MathUtils.lerp(rotationCurrent, rotationTarget, blend);
    for (const pixel of pixels) {
      const bob = moving ? Math.sin(phase * .6 + pixel.userData.phase) * .025 : 0;
      pixel.position.y = pixel.userData.y + bob + (1 - intro) * .7;
      pixel.rotation.set(.18, phase * .10 + pixel.userData.phase, .08);
      pixel.scale.setScalar(isGear ? .6 : intro);
    }

    portraits.forEach((portrait, i) => {
      const active = roles[i] === selected;
      portrait.material.opacity = THREE.MathUtils.lerp(portrait.material.opacity, active ? intro : 0, blend);
      portrait.visible = portrait.material.opacity > .003;
      const targetX = active ? .10 : roles.indexOf(selected) > i ? -.25 : .32;
      portrait.position.x = THREE.MathUtils.lerp(portrait.position.x, targetX, blend);
      portrait.position.y = .17 - .09 * (1 - intro) + drift;
      portrait.rotation.y = world.rotation.y * -.70;
    });

    const entryOffset = (1 - intro) * 1.35;
    const activeRole = selected === 'gear' ? 'voice' : selected;
    const left = [-1.84 - entryOffset, -.86 - entryOffset * .2, 1.25];
    const top = [1.64 + entryOffset, 1.20 + drift * 2, .65];
    const bottom = [1.73 + entryOffset, -1.16 - drift, .85];
    const idleWobble = moving ? Math.sin(phase * .63) * .08 : 0;

    if (isGear) {
      setProp(props.voice, [0, .16, .7], 3.8, [.14, rotationCurrent + idleWobble, -.12], blend);
      setProp(props.chat, [-2.7, -.9, -.2], 0, [-.18, .48, -.20], blend);
      setProp(props.sales, [2.7, -1.2, -.2], 0, [.12, -.45, .12], blend);
    } else {
      const positions = activeRole === 'chat'
        ? {chat: left, sales: bottom, voice: top}
        : activeRole === 'sales'
          ? {chat: bottom, sales: left, voice: top}
          : {chat: top, sales: bottom, voice: left};
      setProp(props.chat, positions.chat, activeRole === 'chat' ? 1.32 : .84,
        [.10, .50 + idleWobble, -.16], blend);
      setProp(props.sales, positions.sales, activeRole === 'sales' ? 1.47 : .95,
        [.10, -.50 + idleWobble, .12], blend);
      setProp(props.voice, positions.voice, activeRole === 'voice' ? 1.64 : 1.02,
        [.15, -.55 + idleWobble, .15], blend);
    }

    renderer.render(scene, camera);
    settleFrames = Math.max(0, settleFrames - 1);
    if (moving || settleFrames > 0) frameRequest = requestAnimationFrame(render);
  }

  function wake() {
    if (disposed) return;
    if (frameRequest) cancelAnimationFrame(frameRequest);
    lastTime = 0;
    frameRequest = requestAnimationFrame(render);
  }

  stage.addEventListener('pointermove', event => {
    if (!finePointer.matches || !isMoving()) return;
    const bounds = stage.getBoundingClientRect();
    pointerX = THREE.MathUtils.clamp((event.clientX - bounds.left) / bounds.width * 2 - 1, -1, 1);
    pointerY = THREE.MathUtils.clamp((event.clientY - bounds.top) / bounds.height * 2 - 1, -1, 1);
  }, {passive: true});
  stage.addEventListener('pointerleave', () => {
    pointerX = 0;
    pointerY = 0;
  });
  stage.addEventListener('viewchange', setView);
  stage.addEventListener('rotateproduct', event => {
    const target = -.53 + event.detail.angle;
    const difference = target - rotationTarget;
    rotationTarget += Math.atan2(Math.sin(difference), Math.cos(difference));
    settleFrames = 55;
    wake();
  });
  window.addEventListener('scroll', () => {
    if (!visible) return;
    scrollDepth = Math.min(1, window.scrollY / Math.max(1, innerHeight * .75));
  }, {passive: true});
  const resizeObserver = new ResizeObserver(sizeCanvas);
  resizeObserver.observe(canvas);
  const visibilityObserver = new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    wake();
  }, {rootMargin: '70px'});
  visibilityObserver.observe(stage);
  document.addEventListener('ambientchange', () => {
    if (!isMoving()) { pointerX = 0; pointerY = 0; }
    wake();
  });
  for (const name of ['visibilitychange', 'filmstate']) {
    document.addEventListener(name, wake);
  }

  canvas.addEventListener('webglcontextlost', event => {
    event.preventDefault();
    disposed = true;
    cancelAnimationFrame(frameRequest);
    resizeObserver.disconnect();
    visibilityObserver.disconnect();
    delete stage.dataset.webgl;
    canvas.hidden = true;
    document.dispatchEvent(new Event('ambientchange'));
  });

  // Prepare the first frame before swapping out the accessible image fallback.
  for (const prop of Object.values(props)) prop.scale.setScalar(.001);
  sizeCanvas();
  setView();
  cancelAnimationFrame(frameRequest);
  frameRequest = 0;
  render(performance.now());
  stage.dataset.webgl = 'ready';
  canvas.hidden = false;
  document.dispatchEvent(new Event('ambientchange'));
}
