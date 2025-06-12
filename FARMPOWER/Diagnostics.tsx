import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AlertTriangle, CheckCircle, Clock, Activity, Settings, FileText } from "lucide-react"
import DiagnosticsChart from "@/components/diagnostics-chart"

export default function DiagnosticsPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container py-4">
          <h1 className="text-3xl font-bold">Remote Diagnostics</h1>
          <p className="text-muted-foreground">Monitor and diagnose your equipment remotely</p>
        </div>
      </header>

      <main className="flex-1 container py-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <Card className="bg-green-50">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle>Healthy</CardTitle>
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <CardDescription>Equipment with no issues</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">3</div>
            </CardContent>
          </Card>

          <Card className="bg-yellow-50">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle>Warnings</CardTitle>
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
              </div>
              <CardDescription>Equipment with minor issues</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">1</div>
            </CardContent>
          </Card>

          <Card className="bg-red-50">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle>Critical</CardTitle>
                <AlertTriangle className="h-5 w-5 text-red-600" />
              </div>
              <CardDescription>Equipment with critical issues</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">0</div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="mb-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="engine">Engine</TabsTrigger>
            <TabsTrigger value="hydraulics">Hydraulics</TabsTrigger>
            <TabsTrigger value="electrical">Electrical</TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Equipment Health Overview</CardTitle>
                    <CardDescription>Real-time monitoring of key systems</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <DiagnosticsChart />
                  </CardContent>
                </Card>
              </div>

              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Recent Alerts</CardTitle>
                    <CardDescription>Last 24 hours</CardDescription>
                  </CardHeader>
                  <CardContent className="p-0">
                    <div className="divide-y">
                      <div className="flex items-start gap-3 p-4">
                        <div className="mt-0.5">
                          <AlertTriangle className="h-5 w-5 text-yellow-500" />
                        </div>
                        <div>
                          <p className="font-medium">Hydraulic Pressure Warning</p>
                          <p className="text-sm text-muted-foreground">Tractor 2 - 2 hours ago</p>
                          <p className="text-sm mt-1">Hydraulic pressure below recommended level</p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3 p-4">
                        <div className="mt-0.5">
                          <Clock className="h-5 w-5 text-blue-500" />
                        </div>
                        <div>
                          <p className="font-medium">Maintenance Reminder</p>
                          <p className="text-sm text-muted-foreground">Harvester 1 - 8 hours ago</p>
                          <p className="text-sm mt-1">Scheduled maintenance due in 50 hours</p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3 p-4">
                        <div className="mt-0.5">
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        </div>
                        <div>
                          <p className="font-medium">Issue Resolved</p>
                          <p className="text-sm text-muted-foreground">Sprayer 1 - 12 hours ago</p>
                          <p className="text-sm mt-1">Fuel filter replaced successfully</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                  <CardFooter className="border-t bg-slate-50">
                    <Button variant="ghost" className="w-full">
                      View All Alerts
                    </Button>
                  </CardFooter>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Quick Actions</CardTitle>
                    <CardDescription>Remote equipment controls</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <Button variant="outline" className="w-full justify-start">
                      <Activity className="mr-2 h-4 w-4" />
                      Run Diagnostic Test
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <Settings className="mr-2 h-4 w-4" />
                      Adjust Settings
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <FileText className="mr-2 h-4 w-4" />
                      Generate Report
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </div>

            <div className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Equipment Status</CardTitle>
                  <CardDescription>Current status of all equipment</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="relative overflow-x-auto">
                    <table className="w-full text-sm text-left">
                      <thead className="text-xs uppercase bg-slate-50">
                        <tr>
                          <th scope="col" className="px-6 py-3">
                            Equipment
                          </th>
                          <th scope="col" className="px-6 py-3">
                            Status
                          </th>
                          <th scope="col" className="px-6 py-3">
                            Engine Hours
                          </th>
                          <th scope="col" className="px-6 py-3">
                            Fuel Level
                          </th>
                          <th scope="col" className="px-6 py-3">
                            Last Maintenance
                          </th>
                          <th scope="col" className="px-6 py-3">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr className="bg-white border-b">
                          <td className="px-6 py-4 font-medium">John Deere 8R Tractor</td>
                          <td className="px-6 py-4">
                            <span className="flex items-center">
                              <span className="w-2 h-2 mr-2 bg-green-500 rounded-full"></span>
                              Operational
                            </span>
                          </td>
                          <td className="px-6 py-4">1,245 hrs</td>
                          <td className="px-6 py-4">85%</td>
                          <td className="px-6 py-4">2 weeks ago</td>
                          <td className="px-6 py-4">
                            <Button variant="link" className="h-auto p-0">
                              View Details
                            </Button>
                          </td>
                        </tr>
                        <tr className="bg-white border-b">
                          <td className="px-6 py-4 font-medium">Case IH Harvester</td>
                          <td className="px-6 py-4">
                            <span className="flex items-center">
                              <span className="w-2 h-2 mr-2 bg-green-500 rounded-full"></span>
                              Operational
                            </span>
                          </td>
                          <td className="px-6 py-4">890 hrs</td>
                          <td className="px-6 py-4">72%</td>
                          <td className="px-6 py-4">1 month ago</td>
                          <td className="px-6 py-4">
                            <Button variant="link" className="h-auto p-0">
                              View Details
                            </Button>
                          </td>
                        </tr>
                        <tr className="bg-white border-b">
                          <td className="px-6 py-4 font-medium">New Holland Sprayer</td>
                          <td className="px-6 py-4">
                            <span className="flex items-center">
                              <span className="w-2 h-2 mr-2 bg-yellow-500 rounded-full"></span>
                              Warning
                            </span>
                          </td>
                          <td className="px-6 py-4">650 hrs</td>
                          <td className="px-6 py-4">45%</td>
                          <td className="px-6 py-4">3 weeks ago</td>
                          <td className="px-6 py-4">
                            <Button variant="link" className="h-auto p-0">
                              View Details
                            </Button>
                          </td>
                        </tr>
                        <tr className="bg-white">
                          <td className="px-6 py-4 font-medium">Kubota Compact Tractor</td>
                          <td className="px-6 py-4">
                            <span className="flex items-center">
                              <span className="w-2 h-2 mr-2 bg-green-500 rounded-full"></span>
                              Operational
                            </span>
                          </td>
                          <td className="px-6 py-4">320 hrs</td>
                          <td className="px-6 py-4">90%</td>
                          <td className="px-6 py-4">1 week ago</td>
                          <td className="px-6 py-4">
                            <Button variant="link" className="h-auto p-0">
                              View Details
                            </Button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="engine">
            <Card>
              <CardHeader>
                <CardTitle>Engine Diagnostics</CardTitle>
                <CardDescription>Detailed engine performance metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[400px] flex items-center justify-center bg-slate-100 rounded-md">
                  <div className="text-center p-6">
                    <p className="text-muted-foreground mb-2">Engine Performance Dashboard</p>
                    <p className="text-sm text-muted-foreground">
                      This dashboard would display detailed engine metrics including temperature, oil pressure, RPM
                      history, and fuel efficiency data.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="hydraulics">
            <Card>
              <CardHeader>
                <CardTitle>Hydraulic System Diagnostics</CardTitle>
                <CardDescription>Detailed hydraulic system metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[400px] flex items-center justify-center bg-slate-100 rounded-md">
                  <div className="text-center p-6">
                    <p className="text-muted-foreground mb-2">Hydraulic System Dashboard</p>
                    <p className="text-sm text-muted-foreground">
                      This dashboard would display detailed hydraulic system metrics including pressure levels, fluid
                      temperature, flow rates, and system integrity data.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="electrical">
            <Card>
              <CardHeader>
                <CardTitle>Electrical System Diagnostics</CardTitle>
                <CardDescription>Detailed electrical system metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[400px] flex items-center justify-center bg-slate-100 rounded-md">
                  <div className="text-center p-6">
                    <p className="text-muted-foreground mb-2">Electrical System Dashboard</p>
                    <p className="text-sm text-muted-foreground">
                      This dashboard would display detailed electrical system metrics including battery health,
                      alternator output, circuit integrity, and sensor data.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
} 