import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import './style.css'
import App from './App.vue'

import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faPlus,
  faTrash,
  faPen,
  faThumbsUp,
  faLock,
  faLink,
  faCopy,
  faGear,
  faXmark,
  faClock,
  faUsers,
  faChevronDown,
  faEye,
  faCheck,
  faArrowRight,
  faColumns,
  faRotate,
  faLightbulb,
  faPencil,
  faMagnifyingGlass,
  faTriangleExclamation,
} from '@fortawesome/free-solid-svg-icons'

library.add(
  faPlus, faTrash, faPen, faThumbsUp, faLock, faLink,
  faCopy, faGear, faXmark, faClock, faUsers, faChevronDown,
  faEye, faCheck, faArrowRight, faColumns,
  faRotate, faLightbulb, faPencil, faMagnifyingGlass,
  faTriangleExclamation,
)

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.component('font-awesome-icon', FontAwesomeIcon)
app.mount('#app')
