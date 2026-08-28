const mongoose = require('mongoose');

const classroomSchema = new mongoose.Schema({
  roomNumber: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  building: {
    type: String,
    required: true,
    trim: true
  },
  floor: {
    type: Number,
    required: true
  },
  capacity: {
    type: Number,
    required: true,
    min: 1
  },
  type: {
    type: String,
    enum: ['lecture_hall', 'laboratory', 'seminar_room', 'computer_lab', 'workshop'],
    required: true
  },
  equipment: [{
    name: String,
    quantity: Number,
    status: {
      type: String,
      enum: ['working', 'maintenance', 'broken'],
      default: 'working'
    }
  }],
  features: [{
    type: String,
    enum: ['projector', 'whiteboard', 'smartboard', 'ac', 'wifi', 'microphone', 'speakers']
  }],
  availability: {
    monday: [{ start: String, end: String }],
    tuesday: [{ start: String, end: String }],
    wednesday: [{ start: String, end: String }],
    thursday: [{ start: String, end: String }],
    friday: [{ start: String, end: String }],
    saturday: [{ start: String, end: String }],
    sunday: [{ start: String, end: String }]
  },
  currentStatus: {
    occupied: {
      type: Boolean,
      default: false
    },
    occupantCount: {
      type: Number,
      default: 0
    },
    temperature: Number,
    humidity: Number,
    lightLevel: Number,
    lastUpdated: {
      type: Date,
      default: Date.now
    }
  },
  maintenanceSchedule: [{
    date: Date,
    type: String,
    description: String,
    status: {
      type: String,
      enum: ['scheduled', 'in_progress', 'completed'],
      default: 'scheduled'
    }
  }],
  isActive: {
    type: Boolean,
    default: true
  }
}, {
  timestamps: true
});

// Indexes for performance
classroomSchema.index({ roomNumber: 1 });
classroomSchema.index({ building: 1, floor: 1 });
classroomSchema.index({ type: 1, capacity: 1 });

module.exports = mongoose.model('Classroom', classroomSchema);
