db.sensors.aggregate([
  {
    $project: {
      sensor_id: 1,
      timestamp: 1,
      power_usage: 1,
      month: { $dateToString: { format: "%Y-%m", date: "$timestamp" } }
    }
  },
  {
    $group: {
      _id: { sensor: "$sensor_id", month: "$month" },
      avgPowerUsage: { $avg: "$power_usage" }
    }
  },
  { $sort: { "_id.month": 1, "_id.sensor": 1 } }
])
