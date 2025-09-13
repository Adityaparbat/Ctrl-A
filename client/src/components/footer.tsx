import { motion } from "framer-motion";

export default function Footer() {
  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <footer className="bg-foreground text-background py-12" role="contentinfo">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-4 gap-8">
          {/* Company Info */}
          <motion.div 
            className="md:col-span-2"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h3 className="text-2xl font-bold mb-4" data-testid="footer-logo">
              <i className="fas fa-universal-access mr-2" aria-hidden="true"></i>
              Inlightex
            </h3>
            <p className="text-gray-300 mb-4 max-w-md" data-testid="footer-description">
              Empowering disabled individuals through innovative technology solutions. Building a more accessible and inclusive digital world for everyone.
            </p>
            <div className="flex space-x-4">
              <motion.a 
                href="#" 
                className="text-gray-300 hover:text-white transition-colors" 
                aria-label="Facebook"
                whileHover={{ scale: 1.2 }}
                data-testid="social-facebook"
              >
                <i className="fab fa-facebook text-xl" aria-hidden="true"></i>
              </motion.a>
              <motion.a 
                href="#" 
                className="text-gray-300 hover:text-white transition-colors" 
                aria-label="Twitter"
                whileHover={{ scale: 1.2 }}
                data-testid="social-twitter"
              >
                <i className="fab fa-twitter text-xl" aria-hidden="true"></i>
              </motion.a>
              <motion.a 
                href="#" 
                className="text-gray-300 hover:text-white transition-colors" 
                aria-label="LinkedIn"
                whileHover={{ scale: 1.2 }}
                data-testid="social-linkedin"
              >
                <i className="fab fa-linkedin text-xl" aria-hidden="true"></i>
              </motion.a>
              <motion.a 
                href="#" 
                className="text-gray-300 hover:text-white transition-colors" 
                aria-label="Instagram"
                whileHover={{ scale: 1.2 }}
                data-testid="social-instagram"
              >
                <i className="fab fa-instagram text-xl" aria-hidden="true"></i>
              </motion.a>
            </div>
          </motion.div>
          
          {/* Quick Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
          >
            <h4 className="text-lg font-semibold mb-4" data-testid="footer-links-title">Quick Links</h4>
            <ul className="space-y-2">
              <li>
                <button 
                  onClick={() => scrollToSection('features')}
                  className="text-gray-300 hover:text-white transition-colors"
                  data-testid="footer-link-features"
                >
                  Features
                </button>
              </li>
              <li>
                <button 
                  onClick={() => scrollToSection('accessibility')}
                  className="text-gray-300 hover:text-white transition-colors"
                  data-testid="footer-link-accessibility"
                >
                  Accessibility
                </button>
              </li>
              <li>
                <a href="#" className="text-gray-300 hover:text-white transition-colors" data-testid="footer-link-pricing">
                  Pricing
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-300 hover:text-white transition-colors" data-testid="footer-link-support">
                  Support
                </a>
              </li>
            </ul>
          </motion.div>
          
          {/* Contact */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            viewport={{ once: true }}
          >
            <h4 className="text-lg font-semibold mb-4" data-testid="footer-contact-title">Contact</h4>
            <ul className="space-y-2 text-gray-300">
              <li data-testid="footer-email">
                <i className="fas fa-envelope mr-2" aria-hidden="true"></i>
                support@inlightex.com
              </li>
              <li data-testid="footer-phone">
                <i className="fas fa-phone mr-2" aria-hidden="true"></i>
                1-800-INLIGHTEX
              </li>
              <li data-testid="footer-location">
                <i className="fas fa-map-marker-alt mr-2" aria-hidden="true"></i>
                India
              </li>
            </ul>
          </motion.div>
        </div>
        
        <motion.div 
          className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-300"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          viewport={{ once: true }}
        >
          <p data-testid="footer-copyright">
            &copy; 2024 Inlightex. All rights reserved. | 
            <a href="#" className="hover:text-white transition-colors ml-1" data-testid="footer-privacy">
              Privacy Policy
            </a> | 
            <a href="#" className="hover:text-white transition-colors ml-1" data-testid="footer-terms">
              Terms of Service
            </a>
          </p>
        </motion.div>
      </div>
    </footer>
  );
}
