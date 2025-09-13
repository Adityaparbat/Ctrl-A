import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowLeft, Mic, Camera, Volume2, MessageSquare, Heart, Accessibility, BookOpen, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Link } from "wouter";

interface DemoFeature {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  category: string;
  interactive: boolean;
}

const demoFeatures: DemoFeature[] = [
  {
    id: "voice-commands",
    title: "Voice Commands",
    description: "Control your device with natural speech patterns",
    icon: Mic,
    category: "input",
    interactive: true
  },
  {
    id: "isl-recognition",
    title: "ISL Recognition",
    description: "Indian Sign Language interpretation and translation",
    icon: MessageSquare,
    category: "input",
    interactive: true
  },
  {
    id: "reading-assistant",
    title: "Reading Assistant",
    description: "AI-powered text-to-speech with comprehension support",
    icon: BookOpen,
    category: "assistance",
    interactive: true
  },
  {
    id: "camera-navigation",
    title: "Camera Navigation",
    description: "Visual scene description for navigation assistance",
    icon: Camera,
    category: "navigation",
    interactive: true
  },
  {
    id: "emergency-support",
    title: "Emergency Support",
    description: "Quick access to emergency services and contacts",
    icon: Shield,
    category: "safety",
    interactive: true
  },
  {
    id: "peer-connections",
    title: "Peer Connections",
    description: "Connect with community members and support groups",
    icon: Heart,
    category: "social",
    interactive: false
  }
];

export default function Demo() {
  const [activeFeature, setActiveFeature] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [demoState, setDemoState] = useState({
    voiceInput: "",
    islDetected: "",
    readingText: "",
    cameraFeedback: "",
    emergencyStatus: "Ready"
  });

  const handleVoiceDemo = () => {
    setIsListening(!isListening);
    if (!isListening) {
      setDemoState(prev => ({ ...prev, voiceInput: "Listening..." }));
      setTimeout(() => {
        setDemoState(prev => ({ 
          ...prev, 
          voiceInput: "Command recognized: 'Open reading assistant'"
        }));
        setIsListening(false);
      }, 3000);
    }
  };

  const handleISLDemo = () => {
    setDemoState(prev => ({ ...prev, islDetected: "Detecting hand gestures..." }));
    setTimeout(() => {
      setDemoState(prev => ({ 
        ...prev, 
        islDetected: "Sign detected: 'Hello' - Converting to speech"
      }));
    }, 2000);
  };

  const handleReadingDemo = () => {
    const sampleText = "Inlightex is empowering accessibility through technology.";
    setDemoState(prev => ({ ...prev, readingText: sampleText }));
    // Simulate text-to-speech
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(sampleText);
      utterance.rate = 0.8;
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleCameraDemo = () => {
    setDemoState(prev => ({ ...prev, cameraFeedback: "Analyzing scene..." }));
    setTimeout(() => {
      setDemoState(prev => ({ 
        ...prev, 
        cameraFeedback: "Scene: Indoor room with door ahead, chair to the right"
      }));
    }, 2000);
  };

  const handleEmergencyDemo = () => {
    setDemoState(prev => ({ ...prev, emergencyStatus: "Emergency services contacted" }));
    setTimeout(() => {
      setDemoState(prev => ({ ...prev, emergencyStatus: "Ready" }));
    }, 3000);
  };

  const renderFeatureDemo = (feature: DemoFeature) => {
    const IconComponent = feature.icon;
    
    return (
      <Card key={feature.id} className="h-full border-2 hover:border-primary/50 transition-colors">
        <CardHeader>
          <div className="flex items-center justify-between">
            <IconComponent className="h-8 w-8 text-primary" />
            <Badge variant="secondary">{feature.category}</Badge>
          </div>
          <CardTitle className="text-xl">{feature.title}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">{feature.description}</p>
          
          {feature.interactive && (
            <div className="space-y-3">
              {feature.id === "voice-commands" && (
                <>
                  <Button 
                    onClick={handleVoiceDemo}
                    className={`w-full ${isListening ? 'bg-red-500 hover:bg-red-600' : ''}`}
                    data-testid={`button-demo-${feature.id}`}
                  >
                    <Mic className="mr-2 h-4 w-4" />
                    {isListening ? "Stop Listening" : "Try Voice Command"}
                  </Button>
                  {demoState.voiceInput && (
                    <div className="p-3 bg-muted rounded-lg text-sm" data-testid="demo-voice-result">
                      {demoState.voiceInput}
                    </div>
                  )}
                </>
              )}
              
              {feature.id === "isl-recognition" && (
                <>
                  <Button 
                    onClick={handleISLDemo}
                    className="w-full"
                    data-testid={`button-demo-${feature.id}`}
                  >
                    <MessageSquare className="mr-2 h-4 w-4" />
                    Try ISL Recognition
                  </Button>
                  {demoState.islDetected && (
                    <div className="p-3 bg-muted rounded-lg text-sm" data-testid="demo-isl-result">
                      {demoState.islDetected}
                    </div>
                  )}
                </>
              )}
              
              {feature.id === "reading-assistant" && (
                <>
                  <Button 
                    onClick={handleReadingDemo}
                    className="w-full"
                    data-testid={`button-demo-${feature.id}`}
                  >
                    <Volume2 className="mr-2 h-4 w-4" />
                    Try Reading Assistant
                  </Button>
                  {demoState.readingText && (
                    <div className="p-3 bg-muted rounded-lg text-sm" data-testid="demo-reading-result">
                      Reading: "{demoState.readingText}"
                    </div>
                  )}
                </>
              )}
              
              {feature.id === "camera-navigation" && (
                <>
                  <Button 
                    onClick={handleCameraDemo}
                    className="w-full"
                    data-testid={`button-demo-${feature.id}`}
                  >
                    <Camera className="mr-2 h-4 w-4" />
                    Try Camera Navigation
                  </Button>
                  {demoState.cameraFeedback && (
                    <div className="p-3 bg-muted rounded-lg text-sm" data-testid="demo-camera-result">
                      {demoState.cameraFeedback}
                    </div>
                  )}
                </>
              )}
              
              {feature.id === "emergency-support" && (
                <>
                  <Button 
                    onClick={handleEmergencyDemo}
                    variant={demoState.emergencyStatus === "Ready" ? "destructive" : "secondary"}
                    className="w-full"
                    data-testid={`button-demo-${feature.id}`}
                  >
                    <Shield className="mr-2 h-4 w-4" />
                    {demoState.emergencyStatus === "Ready" ? "Emergency Demo" : "Processing..."}
                  </Button>
                  {demoState.emergencyStatus !== "Ready" && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800" data-testid="demo-emergency-result">
                      {demoState.emergencyStatus}
                    </div>
                  )}
                </>
              )}
            </div>
          )}
          
          {!feature.interactive && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
              This feature connects you with real community members and support groups.
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  const categories = ["all", "input", "assistance", "navigation", "safety", "social"];

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2" data-testid="link-home">
              <ArrowLeft className="h-5 w-5" />
              <span>Back to Home</span>
            </Link>
            <div className="flex items-center gap-2">
              <Accessibility className="h-6 w-6 text-primary" />
              <span className="font-bold text-lg">Inlightex Demo</span>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-16 bg-gradient-to-r from-primary/10 to-secondary/10">
        <div className="container mx-auto px-4 text-center">
          <motion.h1 
            className="text-4xl md:text-5xl font-bold mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            data-testid="demo-title"
          >
            Experience <span className="text-primary">Accessibility</span> in Action
          </motion.h1>
          <motion.p 
            className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            data-testid="demo-description"
          >
            Explore how Inlightex's accessibility features work in real-time. Try our interactive demos 
            and see how technology can empower everyone.
          </motion.p>
        </div>
      </section>

      {/* Demo Features */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <Tabs defaultValue="all" className="space-y-8">
            <div className="flex justify-center">
              <TabsList className="grid w-full max-w-3xl grid-cols-6" data-testid="demo-category-tabs">
                <TabsTrigger value="all" data-testid="tab-all">All</TabsTrigger>
                <TabsTrigger value="input" data-testid="tab-input">Input</TabsTrigger>
                <TabsTrigger value="assistance" data-testid="tab-assistance">Assist</TabsTrigger>
                <TabsTrigger value="navigation" data-testid="tab-navigation">Navigate</TabsTrigger>
                <TabsTrigger value="safety" data-testid="tab-safety">Safety</TabsTrigger>
                <TabsTrigger value="social" data-testid="tab-social">Social</TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value="all" data-testid="demo-features-all">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {demoFeatures.map(renderFeatureDemo)}
              </div>
            </TabsContent>

            {categories.slice(1).map(category => (
              <TabsContent key={category} value={category} data-testid={`demo-features-${category}`}>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {demoFeatures
                    .filter(feature => feature.category === category)
                    .map(renderFeatureDemo)}
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-muted">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
          <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join thousands of users who are already experiencing the power of accessible technology.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" data-testid="button-get-started">
              Get Started Today
            </Button>
            <Button variant="outline" size="lg" asChild data-testid="button-back-home">
              <Link href="/">Back to Home</Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}