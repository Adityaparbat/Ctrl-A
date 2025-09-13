import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import AuthForms from "./auth-forms";
import { LogOut, User } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function Navigation() {
  const [showLogin, setShowLogin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const { user, isAuthenticated, logout } = useAuth();
  const { toast } = useToast();

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      toast({
        title: "Signed out",
        description: "You have been signed out successfully.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to sign out",
        variant: "destructive",
      });
    }
  };

  return (
    <motion.nav 
      className="fixed top-0 w-full z-50 glass-effect"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      role="navigation" 
      aria-label="Main navigation"
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <motion.div 
            className="flex items-center"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 400, damping: 10 }}
          >
            <div className="flex-shrink-0">
              <h1 className="text-2xl font-bold text-primary">
                <i className="fas fa-universal-access mr-2" aria-hidden="true"></i>
                Inlightex
              </h1>
            </div>
          </motion.div>
          
          {/* Navigation Links */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              <button 
                onClick={() => scrollToSection('features')}
                className="text-foreground hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200" 
                aria-label="Features section"
                data-testid="nav-features"
              >
                Features
              </button>
              <button 
                onClick={() => scrollToSection('accessibility')}
                className="text-foreground hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200" 
                aria-label="Accessibility section"
                data-testid="nav-accessibility"
              >
                Accessibility
              </button>
              <button 
                onClick={() => scrollToSection('about')}
                className="text-foreground hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200" 
                aria-label="About section"
                data-testid="nav-about"
              >
                About
              </button>
            </div>
          </div>
          
          {/* Auth Buttons */}
          <div className="flex items-center space-x-4">
            {isAuthenticated && user ? (
              <>
                <div className="hidden md:flex items-center space-x-2">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-foreground" data-testid="user-welcome">
                    Welcome, {user.username}
                  </span>
                </div>
                <Button 
                  variant="outline"
                  onClick={handleLogout}
                  className="text-foreground hover:text-primary border-border hover:border-primary"
                  aria-label="Sign out of your account"
                  data-testid="button-logout"
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Sign Out
                </Button>
              </>
            ) : (
              <>
                <Button 
                  variant="outline"
                  onClick={() => setShowLogin(true)}
                  className="text-foreground hover:text-primary border-border hover:border-primary"
                  aria-label="Login to your account"
                  data-testid="button-login"
                >
                  Login
                </Button>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button 
                    onClick={() => setShowSignup(true)}
                    className="bg-primary text-primary-foreground hover:bg-primary/90"
                    aria-label="Sign up for a new account"
                    data-testid="button-signup"
                  >
                    Sign Up
                  </Button>
                </motion.div>
              </>
            )}
          </div>
        </div>
      </div>
      
      <AuthForms 
        showLogin={showLogin}
        showSignup={showSignup}
        onClose={() => {
          setShowLogin(false);
          setShowSignup(false);
        }}
      />
    </motion.nav>
  );
}
