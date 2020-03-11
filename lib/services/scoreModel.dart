import 'package:flutter/material.dart';
class Score {
  
  Item getById(int id) => Item(id);
  Item getByPosition(int position) {
    return getById(position);
  }
}

@immutable
class Item {
  final int id;
  final Color color;
  final int price = 42;

  Item(this.id)
      : color = Colors.primaries[id % Colors.primaries.length];

  @override
  int get hashCode => id;

  @override
  bool operator ==(Object other) => other is Item && other.id == id;
}
