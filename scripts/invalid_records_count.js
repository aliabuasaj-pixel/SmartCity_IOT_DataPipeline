db.sensors.aggregate([
  {
    $project: {
      sensor_id: 1,
      invalid_temperature: { $cond: [{ $not: ["$temperature"] }, 1, 0] },
      invalid_pollution: { $cond: [{ $not: ["$pollution_level"] }, 1, 0] },
      invalid_traffic: { $cond: [{ $not: ["$traffic_count"] }, 1, 0] }
    }
  },
  {
    $group: {
      _id: null,
      total_invalid_temperature: { $sum: "$invalid_temperature" },
      total_invalid_pollution: { $sum: "$invalid_pollution" },
      total_invalid_traffic: { $sum: "$invalid_traffic" }
    }
  }
])
