(= (apply-action (move $agent $from $to))
   (do
     (remove-atom &self (at $agent $from))
     (add-atom &self (at $agent $to))
     (add-atom &self (event-kind (move-event $agent $from $to) move))
     (add-atom &self (event-actor (move-event $agent $from $to) $agent))
     (add-atom &self (event-place (move-event $agent $from $to) $to))))
