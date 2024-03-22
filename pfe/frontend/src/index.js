import ReactDOM from 'react-dom/client'
import App from './App'
import { ThemeProvider } from './contexts/theme'
import { Provider } from 'react-redux'
import { store } from './app/store'
import './index.css'

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <ThemeProvider>
    <Provider store={store}>
      <App />
    </Provider>
  </ThemeProvider>,
)


