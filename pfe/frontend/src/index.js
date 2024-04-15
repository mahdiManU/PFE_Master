import ReactDOM from 'react-dom/client'
import App from './App'
import { ThemeProvider } from './contexts/theme'
import { Provider } from 'react-redux'
import { store } from './app/store'
import './index.css'
import { LanguageProvider } from './contexts/language';

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <ThemeProvider>
    <LanguageProvider> {/* Wrap App with LanguageProvider */}
      <Provider store={store}>
        <App />
      </Provider>
    </LanguageProvider>
  </ThemeProvider>,
)


