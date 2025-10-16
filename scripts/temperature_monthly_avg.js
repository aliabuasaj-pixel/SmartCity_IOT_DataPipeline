db.sensors.aggregate([
  {
    $project: {
      sensor_id: 1,
      month: { $dateToString: { format: "%Y-%m", date: "$timestamp" } },
      temperature: 1
    }
  },
  {
    $group: {
      _id: { sensor: "$sensor_id", month: "$month" },
      avgTemperature: { $avg: "$temperature" },
      readingsCount: { $sum: 1 }
    }
  },
  {
    $sort: { "_id.month": 1, "_id.sensor": 1 }
  }
])
