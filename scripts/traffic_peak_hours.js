db.sensors.aggregate([
  {
    $match: { traffic_count: { $exists: true } } // تأكد أن الحقل موجود
  },
  {
    $project: {
      sensor_id: 1,
      hour: { $hour: "$timestamp" },
      traffic_count: 1
    }
  },
  {
    $group: {
      _id: { sensor: "$sensor_id", hour: "$hour" },
      totalTraffic: { $sum: "$traffic_count" }
    }
  },
  {
    $sort: { "_id.sensor": 1, totalTraffic: -1 }
  }
])
