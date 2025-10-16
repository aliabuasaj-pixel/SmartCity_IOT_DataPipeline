db.sensors.aggregate([
  {
    $project: {
      sensor_id: 1,
      timestamp: 1,
      dateOnly: {
        $dateToString: { format: "%Y-%m-%d", date: "$timestamp" }
      }
    }
  },
  {
    $group: {
      _id: { sensor: "$sensor_id", day: "$dateOnly" },
      totalReadings: { $sum: 1 }
    }
  },
  {
    $sort: { "_id.day": 1, "_id.sensor": 1 }
  }
]).toArray().forEach(doc => printjson(doc));
