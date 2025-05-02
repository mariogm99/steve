"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Download, Clock, Dumbbell, Calendar } from "lucide-react"

// Default routine data
const defaultRoutine = {
  week_title: "Your Next Week Routine",
  daily_plan: [
    {
      day: "Monday",
      checklist: [
        {
          habit: "5-min morning mobility routine",
          time: "10:05",
        },
        {
          habit: "Evening foam-rolling (10 min)",
          time: "22:30",
        },
      ],
      fitness_session: {
        type: "mixed",
        duration_min: 52,
        start_time: "19:05",
      },
    },
    {
      day: "Tuesday",
      checklist: [
        {
          habit: "5-min morning mobility routine",
          time: "10:05",
        },
        {
          habit: "Evening foam-rolling (10 min)",
          time: "22:30",
        },
        {
          habit: "Sauna session (15-20 min)",
          time: "18:30",
        },
        {
          habit: "Post-workout protein within 30 min",
          time: "19:57",
        },
      ],
      fitness_session: {
        type: "mixed",
        duration_min: 52,
        start_time: "19:05",
      },
    },
    {
      day: "Wednesday",
      checklist: [
        {
          habit: "5-min morning mobility routine",
          time: "10:05",
        },
        {
          habit: "Evening foam-rolling (10 min)",
          time: "22:30",
        },
      ],
      fitness_session: {
        type: "mixed",
        duration_min: 52,
        start_time: "19:05",
      },
    },
    {
      day: "Thursday",
      checklist: [
        {
          habit: "5-min morning mobility routine",
          time: "10:05",
        },
        {
          habit: "Evening foam-rolling (10 min)",
          time: "22:30",
        },
        {
          habit: "Ice bath / cold plunge (2-3× week)",
          time: "18:30",
        },
        {
          habit: "Post-workout protein within 30 min",
          time: "19:57",
        },
        {
          habit: "Sauna session (15-20 min)",
          time: "18:30",
        },
      ],
      fitness_session: {
        type: "mixed",
        duration_min: 52,
        start_time: "19:05",
      },
    },
    {
      day: "Friday",
      checklist: [
        {
          habit: "5-min morning mobility routine",
          time: "10:05",
        },
        {
          habit: "Evening foam-rolling (10 min)",
          time: "22:30",
        },
      ],
      fitness_session: {
        type: "mixed",
        duration_min: 52,
        start_time: "19:05",
      },
    },
    {
      day: "Saturday",
      checklist: [
        {
          habit: "5-min morning mobility routine",
          time: "10:05",
        },
        {
          habit: "Evening foam-rolling (10 min)",
          time: "22:30",
        },
        {
          habit: "Ice bath / cold plunge (2-3× week)",
          time: "18:30",
        },
        {
          habit: "Post-workout protein within 30 min",
          time: "19:57",
        },
        {
          habit: "Sauna session (15-20 min)",
          time: "18:30",
        },
      ],
      fitness_session: {
        type: "mixed",
        duration_min: 52,
        start_time: "19:05",
      },
    },
    {
      day: "Sunday",
      checklist: [
        {
          habit: "5-min morning mobility routine",
          time: "10:05",
        },
        {
          habit: "Evening foam-rolling (10 min)",
          time: "22:30",
        },
      ],
      fitness_session: {
        type: "mixed",
        duration_min: 52,
        start_time: "19:05",
      },
    },
  ],
}

export default function FitnessRoutineTracker() {
  const [routine, setRoutine] = useState(defaultRoutine)
  const [progress, setProgress] = useState({})
  const [currentDay, setCurrentDay] = useState("")
  const [selectedDay, setSelectedDay] = useState("")
  const [weekStartDate, setWeekStartDate] = useState(new Date())

  // Initialize progress tracking
  useEffect(() => {
    // Get current day
    const date = new Date()
    const dayIndex = date.getDay() === 0 ? 6 : date.getDay() - 1 // Convert to 0-6 where 0 is Monday
    const today = routine.daily_plan[dayIndex].day
    setCurrentDay(today)
    setSelectedDay(today)

    // Calculate the start of the week (Monday)
    const startOfWeek = new Date(date)
    const diff = date.getDate() - date.getDay() + (date.getDay() === 0 ? -6 : 1)
    startOfWeek.setDate(diff)
    setWeekStartDate(startOfWeek)

    // Load progress from localStorage
    const savedProgress = localStorage.getItem("fitnessRoutineProgress")
    if (savedProgress) {
      setProgress(JSON.parse(savedProgress))
    } else {
      // Initialize empty progress for each day and habit
      const initialProgress = {}
      routine.daily_plan.forEach((dayPlan) => {
        initialProgress[dayPlan.day] = {
          habits: {},
          fitness_completed: false,
        }
        dayPlan.checklist.forEach((item, index) => {
          initialProgress[dayPlan.day].habits[index] = false
        })
      })
      setProgress(initialProgress)
      localStorage.setItem("fitnessRoutineProgress", JSON.stringify(initialProgress))
    }
  }, [routine])

  // Save progress to localStorage whenever it changes
  useEffect(() => {
    if (Object.keys(progress).length > 0) {
      localStorage.setItem("fitnessRoutineProgress", JSON.stringify(progress))
    }
  }, [progress])

  const toggleHabit = (day, habitIndex) => {
    setProgress((prev) => {
      const newProgress = { ...prev }
      if (!newProgress[day]) {
        newProgress[day] = { habits: {}, fitness_completed: false }
      }
      if (!newProgress[day].habits) {
        newProgress[day].habits = {}
      }
      newProgress[day].habits[habitIndex] = !newProgress[day].habits[habitIndex]
      return newProgress
    })
  }

  const toggleFitnessSession = (day) => {
    setProgress((prev) => {
      const newProgress = { ...prev }
      if (!newProgress[day]) {
        newProgress[day] = { habits: {}, fitness_completed: false }
      }
      newProgress[day].fitness_completed = !newProgress[day].fitness_completed
      return newProgress
    })
  }

  const calculateDailyProgress = (day) => {
    const dayPlan = routine.daily_plan.find((d) => d.day === day)
    if (!dayPlan || !progress[day]) return 0

    const totalItems = dayPlan.checklist.length + 1 // +1 for fitness session
    let completedItems = 0

    // Count completed habits
    dayPlan.checklist.forEach((_, index) => {
      if (progress[day].habits && progress[day].habits[index]) {
        completedItems++
      }
    })

    // Add fitness session if completed
    if (progress[day].fitness_completed) {
      completedItems++
    }

    return Math.round((completedItems / totalItems) * 100)
  }

  const generateWeeklyReport = () => {
    // Format date range for the report title
    const endOfWeek = new Date(weekStartDate)
    endOfWeek.setDate(weekStartDate.getDate() + 6)

    const formatDate = (date) => {
      return date.toLocaleDateString("en-US", { month: "short", day: "numeric" })
    }

    const weekRange = `${formatDate(weekStartDate)} - ${formatDate(endOfWeek)}`

    // Create report content
    let reportContent = `${routine.week_title}: ${weekRange}\n`
    reportContent += `Generated on: ${new Date().toLocaleDateString()}\n\n`

    // Add habit completion data for each day
    routine.daily_plan.forEach((dayPlan) => {
      const day = dayPlan.day
      reportContent += `\n${day}:\n`

      // Fitness session
      const fitnessStatus = progress[day]?.fitness_completed ? "✓" : "✗"
      reportContent += `  Fitness Session (${dayPlan.fitness_session.type}, ${dayPlan.fitness_session.duration_min} min at ${dayPlan.fitness_session.start_time}): ${fitnessStatus}\n\n`

      // Habits
      reportContent += `  Daily Habits:\n`
      dayPlan.checklist.forEach((item, index) => {
        const status = progress[day]?.habits?.[index] ? "✓" : "✗"
        reportContent += `  - ${item.habit} (${item.time}): ${status}\n`
      })

      reportContent += `\n  Daily completion rate: ${calculateDailyProgress(day)}%\n`
    })

    // Add weekly summary
    const weeklyAverage = routine.daily_plan.reduce((sum, dayPlan) => sum + calculateDailyProgress(dayPlan.day), 0) / 7
    reportContent += `\nWeekly average completion rate: ${Math.round(weeklyAverage)}%\n`

    // Create and download the file
    const blob = new Blob([reportContent], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `fitness-routine-report-${weekStartDate.toISOString().split("T")[0]}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // Load routine from JSON file
  const loadRoutineFromFile = (event) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target.result)
          if (data.daily_plan && Array.isArray(data.daily_plan)) {
            setRoutine(data)

            // Reset progress for new routine
            const newProgress = {}
            data.daily_plan.forEach((dayPlan) => {
              newProgress[dayPlan.day] = {
                habits: {},
                fitness_completed: false,
              }
              dayPlan.checklist.forEach((_, index) => {
                newProgress[dayPlan.day].habits[index] = false
              })
            })
            setProgress(newProgress)
            localStorage.setItem("fitnessRoutineProgress", JSON.stringify(newProgress))
          } else {
            alert("Invalid JSON format. Expected structure with daily_plan array.")
          }
        } catch (error) {
          alert("Error parsing JSON file: " + error.message)
        }
      }
      reader.readAsText(file)
    }
  }

  // Format time to 12-hour format
  const formatTime = (time24) => {
    const [hours, minutes] = time24.split(":")
    const hour = Number.parseInt(hours, 10)
    const ampm = hour >= 12 ? "PM" : "AM"
    const hour12 = hour % 12 || 12
    return `${hour12}:${minutes} ${ampm}`
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex flex-col items-center mb-8">
        <h1 className="text-3xl font-bold mb-2">{routine.week_title}</h1>
        <p className="text-muted-foreground mb-4 flex items-center gap-2">
          <Calendar className="h-4 w-4" />
          Week of {weekStartDate.toLocaleDateString()}
        </p>

        <div className="flex items-center gap-4 mb-6">
          <Button variant="outline" className="flex items-center gap-2">
            <label htmlFor="json-upload" className="cursor-pointer flex items-center gap-2">
              <span>Upload Routine JSON</span>
            </label>
            <input id="json-upload" type="file" accept=".json" className="hidden" onChange={loadRoutineFromFile} />
          </Button>

          <Button onClick={generateWeeklyReport} className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            <span>Download Weekly Report</span>
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Daily Routine</CardTitle>
              <CardDescription>Today is {currentDay}. Check off your completed activities.</CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue={currentDay} onValueChange={setSelectedDay}>
                <TabsList className="grid grid-cols-7 mb-4">
                  {routine.daily_plan.map((dayPlan) => (
                    <TabsTrigger key={dayPlan.day} value={dayPlan.day}>
                      {dayPlan.day.substring(0, 3)}
                    </TabsTrigger>
                  ))}
                </TabsList>

                {routine.daily_plan.map((dayPlan) => (
                  <TabsContent key={dayPlan.day} value={dayPlan.day}>
                    <div className="space-y-6">
                      {/* Fitness Session */}
                      <div className="bg-muted/50 p-4 rounded-lg">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <Dumbbell className="h-5 w-5 text-primary" />
                            <h3 className="font-semibold">Fitness Session</h3>
                          </div>
                          <Checkbox
                            id={`${dayPlan.day}-fitness`}
                            checked={progress[dayPlan.day]?.fitness_completed || false}
                            onCheckedChange={() => toggleFitnessSession(dayPlan.day)}
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div className="flex items-center gap-1">
                            <span className="text-muted-foreground">Type:</span>
                            <Badge variant="outline" className="capitalize">
                              {dayPlan.fitness_session.type}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-1">
                            <Clock className="h-3 w-3 text-muted-foreground" />
                            <span className="text-muted-foreground">Start:</span>
                            <span>{formatTime(dayPlan.fitness_session.start_time)}</span>
                          </div>
                          <div className="flex items-center gap-1 col-span-2">
                            <span className="text-muted-foreground">Duration:</span>
                            <span>{dayPlan.fitness_session.duration_min} minutes</span>
                          </div>
                        </div>
                      </div>

                      {/* Daily Habits */}
                      <div>
                        <h3 className="font-semibold mb-3">Daily Habits</h3>
                        <div className="space-y-3">
                          {dayPlan.checklist.map((item, index) => (
                            <div
                              key={index}
                              className="flex items-center justify-between p-3 rounded-lg hover:bg-muted transition-colors"
                            >
                              <div className="flex items-center gap-3">
                                <Checkbox
                                  id={`${dayPlan.day}-habit-${index}`}
                                  checked={progress[dayPlan.day]?.habits?.[index] || false}
                                  onCheckedChange={() => toggleHabit(dayPlan.day, index)}
                                />
                                <div>
                                  <label
                                    htmlFor={`${dayPlan.day}-habit-${index}`}
                                    className="font-medium cursor-pointer"
                                  >
                                    {item.habit}
                                  </label>
                                </div>
                              </div>
                              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                                <Clock className="h-3 w-3" />
                                <span>{formatTime(item.time)}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                ))}
              </Tabs>
            </CardContent>
          </Card>
        </div>

        <div>
          <Card>
            <CardHeader>
              <CardTitle>Weekly Progress</CardTitle>
              <CardDescription>Your completion rate for each day</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {routine.daily_plan.map((dayPlan) => (
                  <div key={dayPlan.day} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>{dayPlan.day}</span>
                      <span>{calculateDailyProgress(dayPlan.day)}%</span>
                    </div>
                    <Progress value={calculateDailyProgress(dayPlan.day)} />
                  </div>
                ))}
              </div>
            </CardContent>
            <CardFooter>
              <Button variant="outline" className="w-full" onClick={generateWeeklyReport}>
                <Download className="mr-2 h-4 w-4" />
                Download Weekly Report
              </Button>
            </CardFooter>
          </Card>
        </div>
      </div>
    </div>
  )
}
