<template>
  <div ref="container" class="earth-hero"></div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, onActivated, onDeactivated, ref } from 'vue'
import {
  Scene,
  OrthographicCamera,
  WebGLRenderer,
  Group,
  Mesh,
  SphereGeometry,
  ShaderMaterial,
  MeshBasicMaterial,
  Vector3,
  Clock,
  TextureLoader,
  SRGBColorSpace,
  BackSide,
  AdditiveBlending
} from 'three'

const container = ref(null)

let renderer = null
let scene = null
let camera = null
let earthGroup = null
let earth = null
let glow = null
let animationId = null
let resizeObserver = null
let running = false
let clock = null

onMounted(() => {
  if (!container.value) return
  try {
    init()
    startLoop()
  } catch (error) {
    console.error('地球背景初始化失败:', error)
  }
})

onBeforeUnmount(() => {
  stopLoop()
  resizeObserver?.disconnect()
  resizeObserver = null
  if (renderer) {
    renderer.dispose()
    renderer.domElement?.remove()
    renderer = null
  }
})

// 首页用了 keep-alive，切到别的页面时暂停渲染，省 GPU
onDeactivated(stopLoop)
onActivated(() => {
  if (renderer) startLoop()
})

function init() {
  const el = container.value
  const width = el.clientWidth || 1
  const height = el.clientHeight || 1

  scene = new Scene()
  // 用正交相机从远处看球体，避免球心偏移导致相机贴近球面、只剩贴图特写。
  // 视野高度固定为 2 个世界单位，地球半径按屏幕宽度换算。
  camera = new OrthographicCamera(-1, 1, 1, -1, 0.1, 200)
  camera.position.set(0, 0, 30)

  renderer = new WebGLRenderer({ antialias: true, alpha: true })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))
  // 背景透明，露出下层的 CSS 星空
  renderer.setClearColor(0x000000, 0)
  renderer.outputColorSpace = SRGBColorSpace
  el.appendChild(renderer.domElement)

  addEarth()

  resizeObserver = new ResizeObserver(applyLayout)
  resizeObserver.observe(el)
  applyLayout()

  clock = new Clock()
}

function addEarth() {
  earthGroup = new Group()
  // 地轴稍微倾斜一点，看起来更自然
  earthGroup.rotation.z = -0.18
  scene.add(earthGroup)

  const loader = new TextureLoader()
  const dayTexture = loader.load('/textures/earth-day.jpg')
  dayTexture.colorSpace = SRGBColorSpace
  dayTexture.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy())
  const nightTexture = loader.load('/textures/earth-night.png')
  nightTexture.colorSpace = SRGBColorSpace
  nightTexture.anisotropy = dayTexture.anisotropy

  // 日景 + 夜景贴图按太阳方向混合：亮面是白天，暗面透出城市灯光
  const earthMaterial = new ShaderMaterial({
    uniforms: {
      dayTexture: { value: dayTexture },
      nightTexture: { value: nightTexture },
      // 太阳放在屏幕背面偏左上：面向镜头的部分以夜景为主，
      // 只有左上边缘被照亮，同时能看到城市灯光
      sunDirection: { value: new Vector3(-0.75, 0.3, -0.3).normalize() }
    },
    vertexShader: /* glsl */ `
      varying vec2 vUv;
      varying vec3 vWorldNormal;

      void main() {
        vUv = uv;
        vWorldNormal = normalize(mat3(modelMatrix) * normal);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */ `
      uniform sampler2D dayTexture;
      uniform sampler2D nightTexture;
      uniform vec3 sunDirection;

      varying vec2 vUv;
      varying vec3 vWorldNormal;

      void main() {
        float light = dot(normalize(vWorldNormal), normalize(sunDirection));
        vec3 dayColor = texture2D(dayTexture, vUv).rgb;
        // 夜面以城市灯光为主，掺一点点日间地形，避免暗部死黑
        vec3 nightColor = texture2D(nightTexture, vUv).rgb + dayColor * 0.035;

        // 昼夜交界做一段柔和过渡
        float dayMix = smoothstep(-0.18, 0.42, light);
        vec3 color = mix(nightColor, dayColor, dayMix);

        gl_FragColor = vec4(color, 1.0);
        #include <colorspace_fragment>
      }
    `
  })

  earth = new Mesh(new SphereGeometry(1, 128, 128), earthMaterial)
  // 初始转到太平洋一侧：画面以海洋为主，右侧能看到亚洲城市灯光
  earth.rotation.y = -0.6
  earthGroup.add(earth)

  // 大气层：略大的球，只渲染背面，在地球轮廓外形成一圈蓝色辉光
  glow = new Mesh(
    new SphereGeometry(1.035, 96, 96),
    new MeshBasicMaterial({
      color: 0x2f74ff,
      transparent: true,
      opacity: 0.18,
      side: BackSide,
      blending: AdditiveBlending,
      depthWrite: false
    })
  )
  earthGroup.add(glow)

  const halo = new Mesh(
    new SphereGeometry(1.09, 96, 96),
    new MeshBasicMaterial({
      color: 0x1a4fff,
      transparent: true,
      opacity: 0.05,
      side: BackSide,
      blending: AdditiveBlending,
      depthWrite: false
    })
  )
  earthGroup.add(halo)
}

// 正交相机的视野高度（世界单位），地球大小按它换算
const VIEW_HEIGHT = 2

function applyLayout() {
  if (!renderer || !camera || !earthGroup || !container.value) return

  const width = container.value.clientWidth
  const height = container.value.clientHeight
  if (!width || !height) return

  renderer.setSize(width, height, false)

  const aspect = width / height
  const halfWidth = (VIEW_HEIGHT * aspect) / 2
  const halfHeight = VIEW_HEIGHT / 2

  camera.left = -halfWidth
  camera.right = halfWidth
  camera.top = halfHeight
  camera.bottom = -halfHeight
  camera.updateProjectionMatrix()

  // 球体直径约为视口宽度的 1.3 倍，球顶落在视口高度 14% 的位置。
  // 屏幕底部只露出球体的上半部分，和头条官网的构图一致。
  const radius = 0.65 * VIEW_HEIGHT * aspect
  const centerY = halfHeight - 0.14 * VIEW_HEIGHT - radius

  earthGroup.scale.setScalar(radius)
  earthGroup.position.y = centerY
}

function startLoop() {
  if (running || !renderer) return
  running = true
  if (!clock) clock = new Clock()

  const tick = () => {
    if (!running) return
    animationId = requestAnimationFrame(tick)

    earth.rotation.y += 0.0018
    // 大气辉光缓慢呼吸
    glow.material.opacity = 0.16 + Math.sin(clock.elapsedTime * 0.7) * 0.03

    renderer.render(scene, camera)
  }
  tick()
}

function stopLoop() {
  running = false
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
}
</script>

<style scoped>
.earth-hero {
  position: absolute;
  inset: 0;
  z-index: 1;
  overflow: hidden;
  background-color: transparent;
  pointer-events: none;
}

.earth-hero :deep(canvas) {
  display: block;
  width: 100%;
  height: 100%;
}
</style>