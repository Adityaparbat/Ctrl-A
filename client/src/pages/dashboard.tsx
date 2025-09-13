import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  User, 
  Activity, 
  Heart, 
  ArrowLeft, 
  Mic, 
  MessageSquare, 
  BookOpen, 
  Camera, 
  Shield,
  Settings,
  BarChart3
} from "lucide-react";
import { Link } from "wouter";
import { useAuth } from "@/hooks/use-auth";

export default function Dashboard() {
  const { user } = useAuth();

  const quickActions = [
    {
      id: "voice-assistant",
      title: "Voice Assistant",
      description: "Control your device with voice commands",
      icon: Mic,
      color: "bg-blue-500"
    },
    {
      id: "isl-interpreter",
      title: "ISL Interpreter", 
      description: "Sign language recognition and translation",
      icon: MessageSquare,
      color: "bg-green-500"
    },
    {
      id: "reading-assistant",
      title: "Reading Assistant",
      description: "Text-to-speech with comprehension support",
      icon: BookOpen,
      color: "bg-purple-500"
    },
    {
      id: "camera-navigation",
      title: "Camera Navigation",
      description: "Visual scene description for navigation",
      icon: Camera,
      color: "bg-orange-500"
    },
    {
      id: "emergency-support",
      title: "Emergency Support", 
      description: "Quick access to emergency services",
      icon: Shield,
      color: "bg-red-500"
    }
  ];

  const recentActivity = [
    {
      id: 1,
      action: "Used Voice Assistant",
      time: "2 hours ago",
      status: "completed"
    },
    {
      id: 2, 
      action: "Accessed Reading Assistant",
      time: "Yesterday",
      status: "completed"
    },
    {
      id: 3,
      action: "Connected with Support Group",
      time: "2 days ago", 
      status: "completed"
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2" data-testid="link-home">
              <ArrowLeft className="h-5 w-5" />
              <span>Back to Home</span>
            </Link>
            
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <User className="h-5 w-5 text-muted-foreground" />
                <span className="font-medium" data-testid="text-username">
                  {user?.username || "User"}
                </span>
              </div>
              <Button variant="ghost" size="sm" data-testid="button-settings">
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-bold mb-2" data-testid="dashboard-title">
            Welcome back, {user?.username}!
          </h1>
          <p className="text-muted-foreground" data-testid="dashboard-subtitle">
            Your personalized accessibility dashboard is ready to help you navigate the digital world.
          </p>
        </motion.div>

        {/* Quick Actions Grid */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {quickActions.map((action, index) => {
              const IconComponent = action.icon;
              return (
                <motion.div
                  key={action.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="cursor-pointer hover:shadow-md transition-shadow" data-testid={`card-action-${action.id}`}>
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className={`p-2 rounded-lg ${action.color} text-white w-fit`}>
                          <IconComponent className="h-5 w-5" />
                        </div>
                        <Badge variant="secondary">Available</Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <h3 className="font-semibold mb-1">{action.title}</h3>
                      <p className="text-sm text-muted-foreground">
                        {action.description}
                      </p>
                      <Button className="w-full mt-3" variant="outline" size="sm">
                        Launch
                      </Button>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </section>

        {/* Stats and Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Usage Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Usage Statistics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Voice Commands Used</span>
                  <span className="font-semibold" data-testid="stat-voice-commands">47</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Reading Sessions</span>
                  <span className="font-semibold" data-testid="stat-reading-sessions">23</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Navigation Assists</span>
                  <span className="font-semibold" data-testid="stat-navigation-assists">12</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Community Connections</span>
                  <span className="font-semibold" data-testid="stat-community-connections">8</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Recent Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                    <div>
                      <p className="text-sm font-medium">{activity.action}</p>
                      <p className="text-xs text-muted-foreground">{activity.time}</p>
                    </div>
                    <Badge variant="secondary" className="text-xs">
                      {activity.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* CTA Section */}
        <section className="mt-8 text-center">
          <Card className="bg-gradient-to-r from-primary/10 to-secondary/10">
            <CardContent className="py-8">
              <Heart className="h-12 w-12 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Need Help?</h3>
              <p className="text-muted-foreground mb-4">
                Our support team and community are here to assist you 24/7
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button data-testid="button-contact-support">Contact Support</Button>
                <Button variant="outline" data-testid="button-join-community">Join Community</Button>
              </div>
            </CardContent>
          </Card>
        </section>
      </main>
    </div>
  );
}