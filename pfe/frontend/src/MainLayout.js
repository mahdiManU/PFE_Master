import Header from './components/Header/Header';
import ScrollToTop from './components/ScrollToTop/ScrollToTop';
import Footer from './components/Footer/Footer';

const MainLayout = ({ children }) => {
  return (
    <>
      <Header />
      {children}
      <ScrollToTop />
      <Footer />
    </>
  );
}

export default MainLayout;