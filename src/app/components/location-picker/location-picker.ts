import { Component, computed, inject, output, signal } from '@angular/core';
import { Location } from '../../services/location';

@Component({
  imports: [],
  selector: 'app-location-picker',
  styleUrl: './location-picker.css',
  templateUrl: './location-picker.html',
})
export class LocationPicker {
  location = inject(Location);

  // emitted when a full location is picked or removed (e.g. to close a panel)
  changed = output<void>();

  // local choice, starts with the saved location
  departmentKey = signal(this.location.selected()?.departmentKey ?? '');
  municipalityKey = signal(this.location.selected()?.municipalityKey ?? '');
  areaKey = signal(this.location.selected()?.areaKey ?? '');

  department = computed(() =>
    this.location.departments().find((d) => d.key === this.departmentKey()),
  );
  municipality = computed(() =>
    this.department()?.municipalities.find((m) => m.key === this.municipalityKey()),
  );

  constructor() {
    this.location.load();
  }

  selectDepartment(key: string) {
    this.departmentKey.set(key);
    this.municipalityKey.set('');
    this.areaKey.set('');
  }

  selectMunicipality(key: string) {
    this.municipalityKey.set(key);
    this.areaKey.set('');
    // municipalities without zones already have their postal code
    const municipality = this.municipality();
    if (municipality?.postal_code) {
      this.save();
    }
  }

  selectArea(key: string) {
    this.areaKey.set(key);
    if (key) {
      this.save();
    }
  }

  clear() {
    this.selectDepartment('');
    this.location.select(null);
    this.changed.emit();
  }

  private save() {
    const department = this.department();
    const municipality = this.municipality();
    if (!department || !municipality) {
      return;
    }

    const area = municipality.areas.find((a) => a.key === this.areaKey());
    const postalCode = area?.postal_code ?? municipality.postal_code;
    if (!postalCode) {
      return; // municipality split by zones and no zone picked yet
    }

    this.location.select({
      departmentKey: department.key,
      municipalityKey: municipality.key,
      areaKey: area?.key ?? null,
      // "Zona 10, Guatemala" / "Antigua Guatemala, Sacatepéquez"
      label: area
        ? `${area.name}, ${municipality.name}`
        : `${municipality.name}, ${department.name}`,
      postalCode,
    });
    this.changed.emit();
  }
}
